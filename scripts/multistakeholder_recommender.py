import pandas as pd

from app.models import User, Product
from app import create_app
import json
import random as rd
from collections import defaultdict
import numpy as np
from tqdm import tqdm
import csv

from config import Config as Cf
import pickle

CONDITION_FILENAME = 'conditions.csv'
PREDICTIONS_FILENAME = 'predictions.p'

bias_rule_dict = {
    "nutri_score": {
        1: ["A", "B", "C", "D", "E"],
        2: ["A", "B", "C", "D"],
        3: ["A", "B", "C"],
        4: ["A", "B"],
        5: ["A"],
    }
}

nutriscore_to_weight = {
    'A': 5,
    'B': 4,
    'C': 3,
    'D': 2,
    'E': 1,
}

def get_ordered_items(predictions):
    """Return the ordered items for a top-N recommendation for each user from a set of predictions.
    Source: inspired by https://github.com/NicolasHug/Surprise/blob/master/examples/top_n_recommendations.py
    and modified by cvandekerckh for random tie breaking

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...].
    """

    rd.seed(0)

    # First map the predictions to each user.
    ordered_items = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        ordered_items[uid].append((iid, est))

    # Then sort the predictions for each user.
    for uid, user_ratings in ordered_items.items():
        rd.shuffle(user_ratings)
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        ordered_items[uid] = user_ratings

    return ordered_items

def load_conditions():
    df_condition = pd.read_csv(Cf.DATA_PATH_RAW / CONDITION_FILENAME)
    condition_dict = dict(zip(df_condition['condition_id'], df_condition['level_of_bias']))
    print(condition_dict)
    return condition_dict

def get_product_list(ordered_items):
    product_list_per_user = {}
    for uid in ordered_items:
        prediction_list_uid = ordered_items[uid]
        product_list_uid = [
            (Product.query.filter_by(id = product_id).first(), predicted_rating) for product_id, predicted_rating in prediction_list_uid
        ]
        product_list_per_user[uid] = product_list_uid
    return product_list_per_user

def change_order_on_condition(ordered_products, modifier_parameters, bias_type):
    level_of_bias = modifier_parameters['level_of_bias']
    promoted_types = bias_rule_dict[bias_type][level_of_bias]
    promoted_products = []
    unpromoted_products = []
    for product in ordered_products:
        if getattr(product, bias_type) in promoted_types:
            promoted_products.append(product)
        else:
            unpromoted_products.append(product)
    return promoted_products + unpromoted_products

def apply_condition_modifier(product_list_per_user, condition_dict, condition_type='linear_combination'):
    product_list_per_user_modified = {user_id: None for user_id in product_list_per_user}
    if condition_type == 'rank_shift': # obsolete
        for user_id in product_list_per_user:
            ordered_products = product_list_per_user[user_id]
            condition = User.query.filter_by(id = user_id).first().condition_id
            modifier_parameters = condition_dict[condition]
            ordered_products = change_order_on_condition(ordered_products, modifier_parameters, "nutri_score")
            product_list_per_user_modified[user_id] = ordered_products
    elif condition_type == 'linear_combination':
        for user_id in product_list_per_user:
            ordered_products = product_list_per_user[user_id]
            condition = User.query.filter_by(id = user_id).first().condition_id
            beta = float(condition_dict[condition])
            products_modified = [ 
                (product, (1-beta)*predicted_rating + beta*nutriscore_to_weight[product.nutri_score])
                for product, predicted_rating in ordered_products
            ]
            ordered_products_modified = sorted(products_modified, key=lambda x: x[1], reverse=True)
            product_list_per_user_modified[user_id] = ordered_products_modified
    return product_list_per_user_modified


def find_betas():
    # Enter here information about the model, as optimized in create_model
    n_recommendations=Cf.N_RECOMMENDATIONS # number of recommendation items
    k=5 # number of neighbours in content based
    weights='25-25-50' # importance distribution between similarity matrices

    app = create_app()
    with app.app_context():
        with open(Cf.DATA_PATH_OUT / PREDICTIONS_FILENAME, 'rb') as file:
            predictions = pickle.load(file)
        ordered_items = get_ordered_items(predictions)
        product_list_per_user = get_product_list(ordered_items)
        condition_dict = load_conditions()
        betas = np.linspace(0, 0.9999, 500)
        average_nutriscore_over_users = []
        for beta in tqdm(betas, desc="Processing betas"):
            condition_dict_all_forced = {condition_id: beta for condition_id in condition_dict}
            product_list_per_user_modified = apply_condition_modifier(product_list_per_user, condition_dict_all_forced)
            average_nutriscore_recommendation = []
            for user_id in product_list_per_user:
                recommended_products = product_list_per_user_modified[user_id][:n_recommendations]
                nutriscores_recommendation = [nutriscore_to_weight[product.nutri_score] for product, _ in recommended_products]
                average_nutriscore_recommendation.append(np.mean(nutriscores_recommendation))
            average_nutriscore_over_users.append(np.mean(average_nutriscore_recommendation))
        with open(Cf.DATA_PATH_OUT / f'betas_N{n_recommendations}_k{5}_w{weights}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['beta','n_avg'])  # write header
            for item1, item2 in zip(betas, average_nutriscore_over_users):
                writer.writerow([item1, item2])

def create_multistakeholder_recommendation():
    app = create_app()
    with app.app_context():
        with open(Cf.DATA_PATH_OUT / PREDICTIONS_FILENAME, 'rb') as file:
            predictions = pickle.load(file)
        ordered_items = get_ordered_items(predictions)
        product_list_per_user = get_product_list(ordered_items)
        condition_dict = load_conditions()
        product_list_per_user = apply_condition_modifier(product_list_per_user, condition_dict)
        #print(product_list_per_user[44849])
        #print(len(product_list_per_user))
        print(product_list_per_user[96195])
        pickle.dump(product_list_per_user, open(Cf.DATA_PATH_OUT / Cf.MODEL_FILENAME, 'wb'))

def find_users_for_testing():
    df_ratings = pd.read_csv('data/fucam/raw/rating_14_04_2025.csv', delimiter=';')
    df_user_conditions = pd.read_csv('data/fucam/out/users_conditions.csv')

    filtered_conditions = df_user_conditions[
        (df_user_conditions['id'].isin(df_ratings['user_id'])) &
        (df_user_conditions['id'] != 135)
    ]
    df_test = filtered_conditions.drop_duplicates(subset='condition_id')[['id', 'condition_id']]
    df_test = df_test.rename(columns={'id': 'user_id'})
    df_test = df_test.sort_values(by='condition_id').reset_index(drop=True)
    df_test.to_csv('data/fucam/out/user_to_test.csv', index=False)
