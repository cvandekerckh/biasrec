from collections import defaultdict
from surprise import SVD
import random as rd

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
        SVD.__init__(self, n_factors=100, random_state=1)

model = {
  'svd100'  : SVD100,
}