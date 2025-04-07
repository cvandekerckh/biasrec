import random as rd 
import pandas as pd
from config import Config as Cf

USER_FILENAME = 'users.csv'
PRODUCT_FILENAME = 'products.csv'
PRODUCT_SPLIT_FILENAME = 'products_split.csv'

ASSIGNMENTS_FILENAME = 'assignments.csv'

USER_ID_COLUMN_NAME = 'id'
CATEGORY_COLUMN_NAME = 'category'

N_PRODUCT_PER_CATEGORY = 5
SEED_VALUE = 42
rd.seed(SEED_VALUE)

def assign_random_product_for_rating():
    # get user ids
    df_user = pd.read_csv(Cf.DATA_PATH_RAW / USER_FILENAME)
    user_ids = df_user[USER_ID_COLUMN_NAME].tolist()

    df_product = pd.read_csv(Cf.DATA_PATH_RAW / PRODUCT_FILENAME, delimiter=';')

    # Group by 'category' and randomly sample 5 IDs from each group
    sampled_ids = df_product.groupby(CATEGORY_COLUMN_NAME).apply(
        lambda x: x.sample(n=N_PRODUCT_PER_CATEGORY, random_state=SEED_VALUE)
    )
    # Extract the 'ids' column from the sampled rows
    list_of_product_ids = sampled_ids['id'].tolist()

    # Create a random permutation of list_of_ids
    permuted_ids = rd.sample(list_of_product_ids, len(list_of_product_ids))

    # Create a list of tuples for (user_id, product_id) assignments
    assignments = [(user_id, product_id) for user_id in user_ids for product_id in permuted_ids]

    # Create the DataFrame
    df_assignments = pd.DataFrame(assignments, columns=['user_id', 'product_id'])

    df_assignments.to_csv(Cf.DATA_PATH_OUT / ASSIGNMENTS_FILENAME, index=False)

def assign_proportion_based_product_for_rating():
     # get user ids
    df_user = pd.read_csv(Cf.DATA_PATH_RAW / USER_FILENAME, delimiter=';')
    user_ids = df_user[USER_ID_COLUMN_NAME].tolist()

    # get products belonging to phase 1
    df_product_split = pd.read_csv(Cf.DATA_PATH_OUT / PRODUCT_SPLIT_FILENAME, delimiter=';')

    print(df_product_split)
    # assign product to users
    phase1_products = df_product_split[df_product_split['split'] == 'phase1']['id'].tolist()
    df_assignments = pd.DataFrame([(user_id, product) for user_id in user_ids for product in phase1_products], 
                                   columns=['user_id', 'product_id'])    
    df_assignments.to_csv(Cf.DATA_PATH_OUT / ASSIGNMENTS_FILENAME, index=False)

