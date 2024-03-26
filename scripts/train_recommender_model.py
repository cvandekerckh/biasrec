from app.recommend.train import fit_model
from app.recommend.recsys import get_ordered_items

from config import Config as Cf
import pickle


def create_recommender_model():
    ratings_file = Cf.DATA_PATH / 'ratings.csv'
    model, anti_testset = fit_model(ratings_file, Cf.MODEL_NAME)
    predictions = model.test(anti_testset)
    ordered_items = get_ordered_items(predictions)
    pickle.dump(ordered_items, open(Cf.DATA_PATH / Cf.MODEL_FILENAME, 'wb'))