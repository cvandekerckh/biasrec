import pandas as pd

from app.recommend.train import fit_model
from app.recommend.recsys import get_ordered_items
from app.models import User, Product
from app import create_app

from config import Config as Cf
import pickle

CONDITION_FILENAME = 'conditions.csv'
bias_rule_dict = {
    "nutri_score": {
        1: ["A", "B", "C", "D", "E"],
        2: ["A", "B", "C", "D"],
        3: ["A", "B", "C"],
        4: ["A", "B"],
        5: ["A"],
    }
}

def load_conditions():
    df_condition = pd.read_csv(Cf.DATA_PATH_RAW / CONDITION_FILENAME)
    condition_dict = df_condition.set_index("condition_id").to_dict("index")
    return condition_dict

def get_product_list(ordered_items):
    product_list_per_user = {}
    for uid in ordered_items:
        prediction_list_uid = ordered_items[uid]
        product_list_uid = [
            Product.query.filter_by(id = product_id).first() for product_id, _ in prediction_list_uid
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

def apply_condition_modifier(product_list_per_user, condition_dict):
    for user_id in product_list_per_user:
        ordered_products = product_list_per_user[user_id]
        condition = User.query.filter_by(id = user_id).first().condition_id
        modifier_parameters = condition_dict[condition]
        ordered_products = change_order_on_condition(ordered_products, modifier_parameters, "nutri_score")
        product_list_per_user[user_id] = ordered_products
    return product_list_per_user

def create_recommender_model():
    app = create_app()
    with app.app_context():
        ratings_file = Cf.DATA_PATH_RAW / 'ratings.csv'
        model, anti_testset = fit_model(ratings_file, Cf.MODEL_NAME)
        predictions = model.test(anti_testset)
        ordered_items = get_ordered_items(predictions)
        product_list_per_user = get_product_list(ordered_items)
        condition_dict = load_conditions()
        product_list_per_user = apply_condition_modifier(product_list_per_user, condition_dict)
        pickle.dump(product_list_per_user, open(Cf.DATA_PATH_OUT / Cf.MODEL_FILENAME, 'wb'))