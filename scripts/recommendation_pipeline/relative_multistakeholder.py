import pickle
import pandas as pd
import random as rd
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt


from config import Config as Cf
from app import create_app
from app.models import User, Product

rd.seed(42)


# Settings
RATINGS_VERSION = '05_05_2025'
BIAS_TYPE = "mean"
NUTRISCORE_TO_WEIGHT = {
    'A': 5,
    'B': 4,
    'C': 3,
    'D': 2,
    'E': 1,
}
KEEP_BIAS_BELOW = 3.5 # Users have to be bias lower than 3.5
CONDITION_RULE = {
    1: 0.0, # add nothing to 
    2: 0.5, # add 0.5 to the
    3: 1.0, # add 1 to the bias
    4: 1.5, # add 1.5 to the bias. Check that this value + KEEP_BIAS_BELOW <= 5
}
CONDITION_FILENAME = 'conditions.csv'


# Inputs
PREDICTIONS_PATH = Cf.DATA_PATH_OUT / 'versioning' / '4_predictions'
PREDICTIONS_FILENAME = f'predictions_{RATINGS_VERSION}.p'

#Charge le fichier .p contenant les prédictions content-based non biaisées.
def load_predictions():
    with open(PREDICTIONS_PATH / PREDICTIONS_FILENAME, "rb") as f:
        predictions = pickle.load(f)
    return predictions

    
# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
#Transformer une liste d’erreurs continues en distribution discrète (tableau de fréquences).
def compute_error_table(errors, step):
    """
    Compute the bucketed error distribution table in the same format
    as your current code.
    """
    if len(errors) == 0:
        return None

    # Map to integer buckets
    k = np.rint(errors / step).astype(int)

    df = pd.DataFrame({"k": k})
    tbl = df.value_counts("k").sort_index().rename("count").reset_index()

    tbl["error"] = tbl["k"] * step
    total = tbl["count"].sum()
    tbl["prop"] = tbl["count"] / total
    tbl["cum_prop"] = tbl["prop"].cumsum()

    return tbl[["error", "count", "prop", "cum_prop"]]


def print_error_table(tbl):
    """
    Pretty-print the error table with fixed formatting.
    """
    with pd.option_context("display.float_format", "{:.3f}".format):
        print(tbl.to_string(index=False))


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

#Jointure SR ↔ base de données produits, permet d’accéder à nutri_score
#{
  #user_id: [
    #(Product, predicted_rating, nutri_weight),
    #...
  #]
#} --> C’est ici que le second objectif devient manipulable.
def get_product_list(ordered_items):
    product_list_per_user = {}
    for uid in ordered_items:
        prediction_list_uid = ordered_items[uid]
        product_list_uid = [
            (Product.query.filter_by(id = product_id).first(), predicted_rating) for product_id, predicted_rating in prediction_list_uid
        ]
        product_list_uid = [(product, predicted_rating, NUTRISCORE_TO_WEIGHT[product.nutri_score]) for product, predicted_rating in product_list_uid]
        product_list_per_user[uid] = product_list_uid
    return product_list_per_user

#Mesurer le biais nutritionnel d’une recommandation
def compute_bias(recommendation, bias_type):
    if bias_type == "mean":
        recommendation_bias = sum(c for _, _, c in recommendation) / len(recommendation)
    elif bias_type == "min":
        recommendation_bias = np.min([bias for _, _, bias in recommendation])
    return recommendation_bias

#Calculer le biais nutritionnel pour chaque utilisateur.
def get_bias_per_user(product_list_per_user, n_recommendations, bias_type):
    bias_per_user = {}
    for user in product_list_per_user:
        product_list_user = product_list_per_user[user]
        recommendation = product_list_user[:n_recommendations]
        bias_per_user[user] =  compute_bias(recommendation, bias_type)
    return bias_per_user

#Filtrer les utilisateurs exploitables expérimentalement. --> Permet de ne garder que les participants ayant un moins bon profil nutri score 
def get_eligible_users(bias_per_user_unbiased, keep_bias_below):
    eligible_users = []
    for user in bias_per_user_unbiased:
        if bias_per_user_unbiased[user] <= keep_bias_below:
            eligible_users.append(user)
    return eligible_users

def add_linear_bias(product_list_per_user_initial, beta):
    """
    Linearly mix each predicted rating with the NutriScore weight:
        r' = (1 - beta) * predicted + beta * weight
    Then re-rank products per user by r'.
    """
    product_list_per_user_biased = {}
    for user, product_list in product_list_per_user_initial.items():
        biased = []
        for product, predicted_rating, weight in product_list:
            rprime = (1.0 - beta) * predicted_rating + beta * weight
            biased.append((product, rprime, weight))
        biased.sort(key=lambda x: x[1], reverse=True)
        product_list_per_user_biased[user] = biased
    return product_list_per_user_biased

#Simuler : “Si j’applique β à cet utilisateur, quel biais vais-je obtenir ?”
def compute_bias_for_beta(product_list_user, beta, n_recommendations, bias_type):
    """
    product_list_user: list of (product, predicted_rating, weight)
    Returns bias of the top-N after re-ranking by r' = (1-beta)*pred + beta*weight
    """
    # rank by mixed score
    ranked = sorted(
        ((p, (1.0 - beta) * pred + beta * w, w) for (p, pred, w) in product_list_user),
        key=lambda x: x[1],
        reverse=True,
    )
    topn = ranked[:n_recommendations]
    return compute_bias(topn, bias_type), topn

#Trouver le β optimal pour un utilisateur donné et une condition donnée.
#Trouver la valeur de β ∈ [0,1] telle que le Nutri-Score moyen du Top-K soit le plus proche possible de la valeur cible target.
def find_beta_for_user(product_list_user, initial_bias, delta, n_recommendations,
                       bias_type="mean", tol=1e-3, max_iter=30):
    """
    Binary-search beta in [0,1] to get bias(topN(beta)) ~= target.
    Returns (best_beta, best_bias, topN_for_best_beta)
    """
    target = min(5.0, initial_bias + float(delta))  # never exceed 5
    # Evaluate ends
    b0, top0 = compute_bias_for_beta(product_list_user, 0.0, n_recommendations, bias_type)
    b1, top1 = compute_bias_for_beta(product_list_user, 1.0, n_recommendations, bias_type)

    # If already at/above target at beta=0, or function can't increase to target, pick closest end
    candidates = [(0.0, b0, top0), (1.0, b1, top1)]
    if target <= b0 or b1 <= b0 + 1e-9:  # no useful monotonicity or already enough
        best = min(candidates, key=lambda t: abs(t[1] - target))
        return best

    # Monotone (typically) increasing → binary search
    lo, hi = 0.0, 1.0
    best = min(candidates, key=lambda t: abs(t[1] - target))
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        bm, topm = compute_bias_for_beta(product_list_user, mid, n_recommendations, bias_type)
        cand = (mid, bm, topm)
        if abs(bm - target) < abs(best[1] - target):
            best = cand
        # Adjust bounds
        if bm < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return best  # (beta, bias, topN)

#Appliquer le β optimal propre à chaque utilisateur.
def add_linear_bias_per_user(product_list_per_user_initial, beta_per_user):
    """
    Apply per-user beta and re-rank lists.
    Returns dict: user -> [(product, rprime, weight), ...] (full list, re-ranked)
    """
    out = {}
    for user, product_list in product_list_per_user_initial.items():
        beta = beta_per_user.get(user, 0.0)
        ranked = sorted(
            ((p, (1.0 - beta) * pred + beta * w, w) for (p, pred, w) in product_list),
            key=lambda x: x[1],
            reverse=True
        )
        out[user] = ranked
    return out


def create_recommendations():
    app = create_app()
    with app.app_context():
        predictions = load_predictions()
        ordered_items = get_ordered_items(predictions)
        product_list_per_user_initial = get_product_list(ordered_items)

        # Initial bias + eligibility
        bias_per_user_initial = get_bias_per_user(
            product_list_per_user_initial,
            Cf.N_RECOMMENDATIONS,
            BIAS_TYPE
        )
        eligible_users = get_eligible_users(bias_per_user_initial, KEEP_BIAS_BELOW)
        print(f'Eligible users : {len(eligible_users)}/{len(bias_per_user_initial)}')

        # Separate eligible users into the conditions
        df_condition = pd.read_csv(Cf.DATA_PATH_RAW / CONDITION_FILENAME)
        deltas = df_condition['delta'].tolist()
        # - Repeat deltas enough times to cover all users
        repeated = (deltas * (len(eligible_users) // len(deltas) + 1))[:len(eligible_users)]

        # - Shuffle for randomness
        rd.shuffle(repeated)

        # - Pair users → deltas
        assignments = dict(zip(eligible_users, repeated))

        # Per-user beta search
        beta_per_user = {}
        achieved_bias_per_user = {}
        for user, plist in product_list_per_user_initial.items():
            initial_bias = bias_per_user_initial[user]
            if user in eligible_users:
                delta = assignments[user]
                beta, achieved_bias, _ = find_beta_for_user(
                    product_list_user=plist,
                    initial_bias=initial_bias,
                    delta=delta,
                    n_recommendations=Cf.N_RECOMMENDATIONS,
                    bias_type=BIAS_TYPE,
                    tol=1e-3,
                    max_iter=30
                )
            else:
                beta, achieved_bias = 0.0, initial_bias
            beta_per_user[user] = float(beta)
            achieved_bias_per_user[user] = float(achieved_bias)

        # Apply per-user betas to build full re-ranked lists
        product_list_per_user_biased = add_linear_bias_per_user(
            product_list_per_user_initial,
            beta_per_user
        )

        # Compute final bias for reporting (top-N of re-ranked lists)
        bias_per_user_biased = get_bias_per_user(
            product_list_per_user_biased,
            Cf.N_RECOMMENDATIONS,
            BIAS_TYPE
        )

        # List of target biased to achieve for evaluation
        targets = {
            u: min(5.0, bias_per_user_initial[u] + assignments[u]) for u in eligible_users
        }

        # Filter only for eligible users
        eligible_set = set(eligible_users)
        product_list_per_user_initial_eligible = {
            u: lst for u, lst in product_list_per_user_initial.items() if u in eligible_set
        }
        bias_per_user_initial_eligible = {
            u: b for u, b in bias_per_user_initial.items() if u in eligible_set
        }
        targets_eligible = {
            u: t for u, t in targets.items() if u in eligible_set
        }
        product_list_per_user_biased_eligible = {
            u: lst for u, lst in product_list_per_user_biased.items() if u in eligible_set
        }
        bias_per_user_biased_eligible = {
            u: b for u, b in bias_per_user_biased.items() if u in eligible_set
        }

        # Evaluate the performance
        # ---------------------------------------------------------
        # Global evaluation
        # ---------------------------------------------------------

        errors = np.array([
            abs(bias_per_user_biased_eligible[u] - targets_eligible[u])
            for u in targets_eligible.keys()
            if u in bias_per_user_biased_eligible
        ])

        N = Cf.N_RECOMMENDATIONS
        step = 1.0 / N

        tbl_global = compute_error_table(errors, step)
        print("\n=== Global error distribution ===")
        print_error_table(tbl_global)


        # ---------------------------------------------------------
        # Per-assignment evaluation
        # ---------------------------------------------------------

        # Convert {user → delta} dict into {delta → [users]}
        assignments_per_delta = {}
        for user, delta in assignments.items():
            assignments_per_delta.setdefault(delta, []).append(user)

        print("\n=== Error distribution per assignment (per delta) ===")

        for delta, users in sorted(assignments_per_delta.items()):

            errors_delta = np.array([
                abs(bias_per_user_biased_eligible[u] - targets_eligible[u])
                for u in users
                if u in bias_per_user_biased_eligible and u in targets_eligible
            ])

            tbl_delta = compute_error_table(errors_delta, step)

            print(f"\n--- Delta {delta} ---")
            if tbl_delta is None:
                print("No users with computed errors.")
            else:
                print_error_table(tbl_delta)

        # ---------------------------------------------------------
        # Return biased recommendation
        # ---------------------------------------------------------

        biased_recommendation = {}

        for user_id in bias_per_user_initial:
            if user_id in product_list_per_user_biased_eligible:
                biased_recommendation[user_id] = {
                    "eligible": True,
                    "error": abs(bias_per_user_biased_eligible[user_id] - targets_eligible[user_id]),
                    "bias_category":  assignments[user_id],
                    "recommendation_list": product_list_per_user_biased_eligible[user_id][:N],
                }
        
        return biased_recommendation

if __name__ == "__main__":
    biased_recommendations = create_recommendations()
    print(f"{len(biased_recommendations)} recommandations générées")
    with open(Cf.DATA_PATH_OUT / "biased_recommendations_test.p", "wb") as f:
        pickle.dump(biased_recommendations, f)
