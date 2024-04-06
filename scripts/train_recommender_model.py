from app.recommend.train import fit_model
from app.recommend.recsys import get_ordered_items, MMR
from app.models import User, Product
from app import create_app

from config import Config as Cf
import pickle
import pandas as pd


def get_product_list(ordered_items):
    product_list_per_user = {}
    for uid in ordered_items:
        prediction_list_uid = ordered_items[uid]
        product_list_uid = [
            Product.query.filter_by(id = product_id).first() for product_id, _ in prediction_list_uid
        ]
        product_list_per_user[uid] = product_list_uid
    return product_list_per_user

def create_recommender_model():
    app = create_app()
    with app.app_context():
        ratings_file = Cf.DATA_PATH / 'ratings.csv'
    model, anti_testset = fit_model(ratings_file, Cf.MODEL_NAME)
    predictions = model.test(anti_testset)
    ordered_items = get_ordered_items(predictions)
    product_list_per_user = get_product_list(ordered_items)
    pickle.dump(product_list_per_user, open(Cf.DATA_PATH / Cf.MODEL_FILENAME, 'wb'))

def get_user_diversity_factor(user_id, csv_file):
    # Charger le fichier CSV
    df = pd.read_csv(csv_file, delimiter=';')
    
    # Recherche de l'utilisateur dans le DataFrame
    user_row = df[df['id'] == user_id]
    
    # Vérifier si l'utilisateur a été trouvé
    if len(user_row) == 0:
        # Si l'utilisateur n'est pas trouvé, retourner None
        return None
    
    # Récupérer le diversity_factor de l'utilisateur
    user_diversity_factor = user_row['diversity_factor'].values[0]
    
    return user_diversity_factor

def create_recommender_model2(user_id):
    ratings_file = Cf.DATA_PATH / 'ratings.csv'
    model, anti_testset = fit_model(ratings_file, Cf.MODEL_NAME)
    predictions = model.test(anti_testset)
    user_diversity_factor = get_user_diversity_factor(user_id, 'users.csv')
    ordered_items = MMR(user_id, user_diversity_factor, Cf.N_RECOMMENDATIONS, predictions)
    product_list_per_user = get_product_list(ordered_items) #utile ou non ?
    pickle.dump(product_list_per_user, open(Cf.DATA_PATH / Cf.MODEL_FILENAME, 'wb'))