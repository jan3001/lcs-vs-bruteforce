import time

class SequenceComparer:
    def __init__(self, sequence_file):
        # Initialize and load sequences from a file
        self.sequences = self.load_sequences(sequence_file)
        if self.sequences:
            # Print loaded sequences
            print("Loaded Sequences:")
            for i, seq in enumerate(self.sequences):
                print(f"S{i+1}: {seq}")
            # Evaluate all pairs of sequences for LCS using dynamic programming and brute force methods
            self.dp_metrics, self.brute_metrics = self.evaluate_all_pairs()

    def load_sequences(self, file_path):
        # Attempt to load sequences from the specified file path
        try:
            with open(file_path, 'r') as file:
                lines = file.read().splitlines()
            sequences = []
            valid_chars = {'A', 'T', 'G', 'C'}
            # Process each line to extract sequences
            for line in lines:
                parts = line.split('=')
                if len(parts) != 2:
                    raise ValueError(f"Invalid format in line: {line}. Expected format: 'Label = Sequence'")
                label, sequence = parts[0].strip(), parts[1].strip()
                if any(char not in valid_chars for char in sequence):
                    raise ValueError(f"Invalid sequence detected in {label}: {sequence}. Only 'A', 'T', 'G', 'C' are allowed.")
                sequences.append(sequence)
            return sequences
        except FileNotFoundError:
            # Handle file not found error
            print("File not found. Please check the path and try again.")
            return None

    def evaluate_all_pairs(self):
        # Evaluate LCS for all pairs of sequences
        dynamic_results = {}
        brute_force_results = {}
        for i in range(len(self.sequences)):
            for j in range(i + 1, len(self.sequences)):
                # Compute LCS using dynamic programming
                lcs_dp, time_dp, comparisons_dp, len1, len2, dp_table = self.calculate_lcs_dp(self.sequences[i], self.sequences[j])
                # Compute LCS using brute force method
                lcs_bf, time_bf, comparisons_bf, _, _ = self.calculate_lcs_brute(self.sequences[i], self.sequences[j], 120, i, j)

                # Print the results and DP table for each pair
                print(f"\nProcessing LCS for Pair S{i+1}-S{j+1}")
                print(f"Sequence 1 (Length {len1}): {self.sequences[i]}")
                print(f"Sequence 2 (Length {len2}): {self.sequences[j]}")
                print("DP Table:")
                for row in dp_table:
                    print(row)
                print(f"DP: '{lcs_dp}', Time={time_dp:.4f}s, Comparisons={comparisons_dp}")
                print(f"BF: '{lcs_bf}', Time={time_bf:.4f}s, Comparisons={comparisons_bf}")

                # Store the results in dictionaries
                dynamic_results[(i, j)] = (lcs_dp, time_dp, comparisons_dp, len1, len2)
                brute_force_results[(i, j)] = (lcs_bf, time_bf, comparisons_bf, len1, len2)
        return dynamic_results, brute_force_results

    def calculate_lcs_dp(self, seq1, seq2):
        # Calculate the LCS using dynamic programming
        start_time = time.time()
        len1, len2 = len(seq1), len(seq2)
        table = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        comparisons = 0

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                comparisons += 1
                if seq1[i - 1] == seq2[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                else:
                    table[i][j] = max(table[i - 1][j], table[i][j - 1])

        # Reconstruct LCS from the DP table
        lcs = self.reconstruct_lcs(seq1, seq2, table, len1, len2)
        time_taken = time.time() - start_time
        return lcs, time_taken, comparisons, len1, len2, table

    def reconstruct_lcs(self, seq1, seq2, table, len1, len2):
        # Reconstruct LCS from the DP table
        lcs = ""
        while len1 > 0 and len2 > 0:
            if seq1[len1 - 1] == seq2[len2 - 1]:
                lcs = seq1[len1 - 1] + lcs
                len1 -= 1
                len2 -= 1
            elif table[len1 - 1][len2] >= table[len1][len2 - 1]:
                len1 -= 1
            else:
                len2 -= 1
        return lcs


    def calculate_lcs_brute(self, seq1, seq2, time_limit, index1, index2):
        start_time = time.time()  # Capture the start time to enforce a time limit
        len1, len2 = len(seq1), len(seq2)  # Store the lengths of both sequences for return values
        subsequences = self.generate_subsequences(seq1)  # Generate all possible subsequences from the first sequence
        longest = ""  # Initialize the longest common subsequence found to an empty string
        total_comparisons = 0  # Initialize the count of comparisons made during the search
        subseq_count = 0  # Initialize the count of subsequences checked

        for subseq in subsequences:
            current_time = time.time()  # Get the current time to check against the time limit
            if current_time - start_time > time_limit:
                # If the time limit is exceeded, print a message and break the loop
                print(f"Brute force time limit exceeded for S{index1+1}-S{index2+1} after examining {subseq_count} subsequences.")
                break
            if len(subseq) <= len(longest):
                # Skip subsequences shorter than the longest found so far
                continue
            is_common, comparisons = self.is_common_subseq(subseq, [seq1, seq2])  # Check if the subsequence is common to both sequences
            total_comparisons += comparisons  # Update total comparisons count
            subseq_count += 1  # Increment the subsequence count
            if len(subseq) > len(longest) and is_common:
                # Update the longest subsequence if the current one is longer and common
                longest = subseq

        time_taken = current_time - start_time  # Calculate total time taken for the brute force method
        return longest, time_taken, total_comparisons, len1, len2  # Return the results



    def generate_subsequences(self, sequence):
        if not sequence:
            # Base case for the recursion: return an empty subsequence
            yield ""
        else:
            first, rest = sequence[0], sequence[1:]  # Split the sequence into first character and the rest
            for sub in self.generate_subsequences(rest):
                # Recursive call to generate all subsequences from the rest of the sequence
                yield sub  # Yield each subsequence as is
                yield first + sub  # Yield subsequences including the first character


    def is_common_subseq(self, subseq, sequences):
        total_comparisons = 0
        for seq in sequences:
            idx = 0
            for char in seq:
                total_comparisons += 1
                if idx == len(subseq):
                    break
                if char == subseq[idx]:
                    idx += 1
            if idx < len(subseq):
                return False, total_comparisons
        return True, total_comparisons

    def display_results(self):
        headers = ['Sequence Pair', 'Length 1', 'Length 2', 'LCS DP', 'Time DP (s)', 'Comparisons DP', 'LCS BF', 'Time BF (s)', 'Comparisons BF']
        header_format = "{:<15} {:<8} {:<8} {:<27} {:<12} {:<15} {:<27} {:<12} {}"
        print(header_format.format(*headers))
        print("-" * 135)
        for key, (lcs_dp, time_dp, comp_dp, len1, len2) in self.dp_metrics.items():
            lcs_bf, time_bf, comp_bf, _, _ = self.brute_metrics[key]  # This assumes the lengths are the same as in dp_metrics and need not be repeated
            print(header_format.format(
                f'S{key[0]+1}-S{key[1]+1}',
                len1,
                len2,
                lcs_dp if lcs_dp is not None else "",
                f'{time_dp:.4f}',
                comp_dp,
                lcs_bf if lcs_bf is not None else "",
                f'{time_bf:.4f}',
                comp_bf
            ))


def main():
    sequence_file = input("Please enter the input file path: ")
    comparer = SequenceComparer(sequence_file)
    if comparer.sequences:
        comparer.display_results()

if __name__ == "__main__":
    main()
