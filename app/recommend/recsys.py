from collections import defaultdict
from surprise import SVD
import math
import random as rd
import pandas as pd
from config import Config as Cf

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

class SVD100(SVD):
    def __init__(self):
        SVD.__init__(self, n_factors=50, n_epochs=50, reg_all=0.1, random_state=1)


def MMR(user_id, diversity_factor, num_recommandations, predictions):
    #Scores de prédiction pour tous les articles
    #predictions = model.predict_anti_testset()    #anti_testset = items not rated
    items = []
    user_estimations = {}
    for prediction in predictions:
        u_id = prediction.uid
        item_id = prediction.iid
        if u_id == user_id :
            if item_id not in [1080,260,1387,1380,1214,1196,1258,858,1210,616,344,2571,593,356,480,780,253,318,595,1,4973,4993,4226,7361,3793,4896,8874,4878,6539,4306,88163,79132,91529,97921,84152,109487,83134,99114,98809,76093] :
                items.append(item_id)
                user_estimations[item_id] = prediction.est
    items = set(items)
    #print(len(items), "\n")
    #print(items)
    #print(len(user_estimations))
    #print(user_estimations)
    
    #Lire la matrice de similarité à partir du fichier CSV
    similarity_file = Cf.DATA_PATH / 'cosine_similarity_matrix_finale.csv'
    matrice_sim = pd.read_csv(similarity_file)
    matrice_sim.index = matrice_sim.columns
    #print(matrice_sim)
    
    selected = {}
    while len(selected) < num_recommandations :
        remaining = items - set(selected)
        maximum = -math.inf
        next_selected = None
        for iid in remaining :
            mmr_score = (1-diversity_factor)*user_estimations[iid] - diversity_factor*max([matrice_sim.loc[str(iid), str(y)] for y in set(selected)-{iid}], default=0)
            #print((iid,mmr_score))
            
            if mmr_score > maximum :
                maximum = mmr_score
                next_selected = iid
                #print((next_selected,maximum))
        selected[next_selected] = maximum

    return selected        

class LatentFactorModel(SVD):
    def __init__(self, n_factors=50, n_epochs=50, reg_all=0.1, random_state=1):
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.reg_all = reg_all
        self.random_state = random_state
        self.model = None

model = {
  'svd100'  : SVD100,
  'LatentFactorModel' : LatentFactorModel,
}