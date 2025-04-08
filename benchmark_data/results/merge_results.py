import os
import re
import pandas as pd
from collections import defaultdict

def merge_csvs_by_prefix(directory, output_directory):
    pattern = re.compile(r'^(.*)_(epoch_\d+|best)\.csv$')
    groups = defaultdict(list)

    # Group files by prefix
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            match = pattern.match(filename)
            if match:
                prefix, epoch = match.groups()
                groups[prefix].append((epoch, filename))

    # Process each group separately
    for prefix, files in groups.items():
        merged_df = pd.DataFrame()
        files.sort(key=lambda x: int(x[0].split('_')[1]) if '_' in x[0] else -1)

        for epoch, filename in files:
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            df = df.set_index('strategy')
            df.columns = [epoch]

            if merged_df.empty:
                merged_df = df
            else:
                merged_df = merged_df.join(df, how='outer')

        # Reset index to have 'strategy' as a column
        merged_df.reset_index(inplace=True)
        output_filename = f"{prefix}_merged.csv"
        output_path = os.path.join(output_directory, output_filename)
        merged_df.to_csv(output_path, index=False)
        print(f"Merged file saved to: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Merge CSVs by prefix")
    parser.add_argument("directory", help="Directory containing CSV files")
    parser.add_argument("output_directory", help="Directory containing CSV files")
    args = parser.parse_args()

    os.makedirs(args.output_directory, exist_ok=True)
    merge_csvs_by_prefix(args.directory, args.output_directory)
