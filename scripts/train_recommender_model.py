from app.recommend.train import fit_model
from app.recommend.recsys import get_top_n

from config import Config as Cf
import pickle


def create_recommender_model():
    ratings_file = Cf.DATA_PATH / 'ratings.csv'
    model, anti_testset = fit_model(ratings_file, Cf.MODEL_NAME)
    predictions = model.test(anti_testset)
    print(predictions)
    top_n = get_top_n(predictions, Cf.N_RECOMMENDATIONS)
    pickle.dump(top_n, open(Cf.DATA_PATH / Cf.MODEL_FILENAME, 'wb'))