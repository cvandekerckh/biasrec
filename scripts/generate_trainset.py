import pandas as pd
import numpy as np
from collections import defaultdict
from config import Config as Cf

def select_random_products(file_path, seed=42, sample_frac=0.1):
    # Load CSV file
    df = pd.read_csv(file_path, delimiter=";")
    
    # Ensure necessary columns exist
    required_columns = {'id', 'category', 'nutri_score'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV file must contain columns: {required_columns}")
    
    # Merge nutri_score E into D
    df['nutri_score'] = df['nutri_score'].replace('E', 'D')
    
    # Group by category and nutri_score
    grouped = df.groupby(['category', 'nutri_score'])
    
    # Initialize result structures
    category_stats = []
    selected_dict = defaultdict(list)
    selected_ids = []
    
    # Set seed for reproducibility
    np.random.seed(seed)
    
    # Iterate through each group
    for (category, nutri_score), group in grouped:
        total_count = len(group)
        sample_size = int(total_count * sample_frac)  # Ensure at least 1 sample per group if not empty
        sampled = group.sample(n=sample_size, random_state=seed)
        
        # Store results
        category_stats.append({'category': category, 'nutri_score': nutri_score, 'count': total_count})
        selected_dict[(category, nutri_score)] = sampled['id'].tolist()
        selected_ids.extend(sampled['id'].tolist())
    
    # Convert category statistics to DataFrame
    category_df = pd.DataFrame(category_stats)
    
    # Shuffle final selected IDs
    np.random.shuffle(selected_ids)
    
    return category_df, selected_dict, selected_ids, df

def generate_trainset():
    sample_frac= 0.15
    seed=42
    PRODUCTS_FILENAME='products.csv'
    PRODUCTS_SPLIT_FILENAME='products_split.csv'

    category_df, selected_dict, selected_ids, df = select_random_products(
        Cf.DATA_PATH_RAW / PRODUCTS_FILENAME,
        seed=seed,
        sample_frac=sample_frac,
    )

    # Display info
    print(category_df)
    print(category_df.groupby('nutri_score').sum())
    print(selected_dict)
    print(len(selected_ids))

    # Store info
    df['split'] = df['id'].apply(lambda x: 'phase1' if x in selected_ids else 'phase2')
    df[['id', 'split']].to_csv(
        Cf.DATA_PATH_OUT / PRODUCTS_SPLIT_FILENAME,
        sep=';',
        index=False,
    )
