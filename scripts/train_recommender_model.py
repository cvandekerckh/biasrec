from app.recommend.train import fit_model
from app.recommend.recsys import get_ordered_items
from app.models import User, Product
from app import create_app

from config import Config as Cf
import pickle


def get_product_list(ordered_items):
    app = create_app()
    with app.app_context():
        product_list_per_user = {}
        for uid in ordered_items:
            prediction_list_uid = ordered_items[uid]
            product_list_uid = [
                Product.query.filter_by(id = product_id).first() for product_id, _ in prediction_list_uid
            ]
            product_list_per_user[uid] = product_list_uid
        return product_list_per_user


def create_recommender_model():
    ratings_file = Cf.DATA_PATH / 'ratings.csv'
    model, anti_testset = fit_model(ratings_file, Cf.MODEL_NAME)
    predictions = model.test(anti_testset)
    ordered_items = get_ordered_items(predictions)
    product_list_per_user = get_product_list(ordered_items)
    pickle.dump(product_list_per_user, open(Cf.DATA_PATH / Cf.MODEL_FILENAME, 'wb'))