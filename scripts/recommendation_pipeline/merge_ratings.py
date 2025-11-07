import pandas as pd
import csv
from pathlib import Path

# === Configuration ===
FILENAMES_TO_MERGE = [
    'rating_14_04_2025.csv',
    'rating_23_04_2025.csv',
    'rating_25_04_2025.csv',
    'rating_05_05_2025.csv'
]

DATA_PATH_IN = Path('data/fucam/raw/ratings')
DATA_PATH_OUT = Path('data/fucam/out/versioning/ratings_merged')
FILENAME_OUT = 'rating_05_05_2025_merged.csv'

def main():

    dfs = []

    for filename in FILENAMES_TO_MERGE:
        file_path = DATA_PATH_IN / filename

        # Auto-detect delimiter
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
            except csv.Error:
                delimiter = ','

        df = pd.read_csv(file_path, delimiter=delimiter)
        df['source_file'] = filename
        dfs.append(df)

    # Combine all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)

    # Drop exact duplicates
    merged_df = merged_df.drop_duplicates()

    # Drop conflicting ratings for user_id == 135
    conflict_check_df = merged_df.copy()

    conflicts_info = []
    resolved_rows = []

    # Group to check for conflicting ratings
    grouped = conflict_check_df.groupby(['user_id', 'product_id'])

    for (user_id, product_id), group in grouped:
        if group['rating'].nunique() > 1:
            if user_id == 135:
                print(f"Conflict for user_id 135 on product_id {product_id}. Ignoring this user's entries.")
                continue
            else:
                print(f"Conflict for user_id {user_id} on product_id {product_id}:")
                for _, row in group.iterrows():
                    print(f"  rating={row['rating']} from {row['source_file']}, id={row.get('id', 'N/A')}")

                # Keep the row with the highest Id (if Id exists), else take the last one
                if 'id' in group.columns:
                    resolved_row = group.loc[group['id'].idxmax()]
                else:
                    resolved_row = group.iloc[-1]  # Fallback
                resolved_rows.append(resolved_row)
        else:
            resolved_rows.append(group.iloc[0])  # No conflict

    # Create final DataFrame, drop user 135 entirely from result
    final_df = pd.DataFrame(resolved_rows)
    final_df = final_df[final_df['user_id'] != 135]

    # Drop unused columns
    columns_to_keep = ['user_id', 'product_id', 'rating']
    final_df = final_df[columns_to_keep]

    # Save result
    output_path = DATA_PATH_OUT / FILENAME_OUT
    final_df.to_csv(output_path, index=False)
    print(f"\nMerged file saved at '{output_path}' with {len(final_df)} rows.")
