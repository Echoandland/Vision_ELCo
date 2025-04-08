import argparse
import pandas as pd
from pathlib import Path
from collections import defaultdict

def aggregate_accuracy(directory: Path):
    """
    Aggregates accuracy values row-wise from `_merged.csv` files in a given directory,
    grouped by the prefix before the first underscore in their filenames.
    """
    csv_files = sorted(directory.glob("*_merged.csv"))  # Ensure consistent order
    
    if not csv_files:
        print(f"No matching files found in {directory}")
        return {}

    grouped_files = defaultdict(list)
    for file in csv_files:
        prefix = file.name.split('_')[0]
        grouped_files[prefix].append(file)

    results = {}

    for prefix, files in grouped_files.items():
        dataframes = []

        for file in files:
            df = pd.read_csv(file)
            df = df.set_index('strategy')
            if "best" in df.columns:
                df = df[['best']].rename(columns={'best': 'accuracy'})
                dataframes.append(df)
            else:
                print(f"Warning: 'best' column not found in {file.name}")

        if not dataframes:
            print(f"No valid accuracy data for group '{prefix}' in {directory}")
            continue

        combined_df = pd.concat(dataframes, axis=1)
        combined_df["mean_accuracy"] = combined_df.filter(like="accuracy").mean(axis=1)
        combined_df["std_accuracy"] = combined_df.filter(like="accuracy").std(axis=1)
        combined_df = combined_df.drop(columns=[col for col in combined_df.columns if col.startswith('accuracy')])

        combined_df = combined_df.round(1)

        # Move 'Overall' row to the bottom if it exists
        if 'Overall' in combined_df.index:
            overall_row = combined_df.loc[['Overall']]
            combined_df = combined_df.drop(index='Overall')
            combined_df = pd.concat([combined_df, overall_row])

        output_file = directory / f"{prefix}_aggregated.csv"
        combined_df.to_csv(output_file, index=True)

        print(f"Aggregated results for group '{prefix}' saved to {output_file}")
        results[prefix] = combined_df.add_prefix(f"{prefix}_")
    return results

def batch_aggregate_accuracy(parent_directory: str):
    """Processes all subdirectories and combines row-wise aggregated results into a final CSV."""
    parent_path = Path(parent_directory)

    if not parent_path.is_dir():
        print(f"Error: {parent_directory} is not a valid directory.")
        return

    aggregated_dfs = []

    for subdir in sorted(parent_path.iterdir()):  # Ensure consistent order
        if subdir.is_dir() and "merged" in subdir.name:
            model = subdir.name.rsplit('-', maxsplit=1)[0]
            group_results = aggregate_accuracy(subdir)
            for df in group_results.values():
                aggregated_dfs.append(df.add_prefix(model + '-'))

    if aggregated_dfs:
        # Merge on index (`strategy`)
        final_df = pd.concat(aggregated_dfs, axis=1)

        # Move 'Overall' row to the bottom if it exists
        if 'Overall' in final_df.index:
            overall_row = final_df.loc[['Overall']]
            final_df = final_df.drop(index='Overall')
            final_df = pd.concat([final_df, overall_row])

        final_output_file = parent_path / "final_aggregated.csv"
        final_df.to_csv(final_output_file, index=True)
        print(f"Final aggregated results saved to {final_output_file}")
    else:
        print("No aggregated data to combine.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch aggregate accuracy and create a final combined CSV.")
    parser.add_argument("parent_directory", type=str, help="Path to the parent directory containing subdirectories.")
    
    args = parser.parse_args()
    batch_aggregate_accuracy(args.parent_directory)
