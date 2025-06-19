import pandas as pd
import pickle
from pathlib import Path
from collections import defaultdict
import numpy as np

def load_data():
    # === Définir les chemins ===
    base_path = Path("C:/Users/camcharles/OneDrive - UCL/Documents/code/biasrec/data/fucam/out")

    recommendation_file = base_path / "versioning" / "predictions" / "predictions_05_05_2025.p"
    similarity_file = base_path / "versioning" / "similarity_matrix" / "similarity_matrix_23_04_2025.csv"
    user_conditions_file = base_path / "users_conditions.csv"

    # === Chargement des recommandations ===
    with open(recommendation_file, "rb") as f:
        predictions = pickle.load(f)

    print("Nombre total de prédictions :", len(predictions))
    print("Exemple de prédiction :", predictions[0])

    user_ids = set([p[0] for p in predictions])
    product_ids = set([p[1] for p in predictions])

    print(f"Nombre d'utilisateurs uniques : {len(user_ids)}")
    print(f"Nombre de produits recommandés au total : {len(product_ids)}")

    # === Matrice de similarité ===
    similarity_matrix = pd.read_csv(similarity_file, index_col=0)
    similarity_matrix.index = similarity_matrix.index.astype(str)
    similarity_matrix.columns = similarity_matrix.columns.astype(str)

    print("\nDimensions de la matrice de similarité :", similarity_matrix.shape)
    print("Extrait matrice :")
    print(similarity_matrix.iloc[:3, :3])

    # === Données expérimentales utilisateurs ===
    user_conditions = pd.read_csv(user_conditions_file, sep=";")
    print("\nExtrait des conditions expérimentales :")
    print(user_conditions.head())

    return predictions, similarity_matrix, user_conditions

#Regrouper les Top-5 recommandations par utilisateur
def group_top_predictions_by_user(predictions, top_n=5):
    user_recommendations = defaultdict(list)
    for user_id, product_id, _, rating, _ in predictions:
        user_recommendations[user_id].append((product_id, rating))

    top_recommendations = {}
    for user_id, items in user_recommendations.items():
        sorted_items = sorted(items, key=lambda x: x[1], reverse=True)[:top_n]
        top_recommendations[user_id] = [str(pid) for pid, _ in sorted_items]  # important : .astype(str)
    return top_recommendations

#Calculer l’ILD pour une liste de produits (formule officielle 26.3.2)
def compute_ILD(product_list, similarity_matrix):
    n = len(product_list)
    if n < 2:
        return 0.0

    total_distance = 0
    count = 0

    for i in range(n):
        for j in range(n):
            if i != j:
                pid1 = product_list[i]
                pid2 = product_list[j]
                try:
                    sim = similarity_matrix.at[pid1, pid2]
                except KeyError:
                    sim = 0  # similarité inconnue = dissimilarité max
                total_distance += (1 - sim)
                count += 1

    return total_distance / count if count > 0 else 0.0

def compute_ILD_per_user(top_recommendations, similarity_matrix):
    ild_scores = {}
    for user_id, product_list in top_recommendations.items():
        ild = compute_ILD(product_list, similarity_matrix)
        ild_scores[user_id] = ild
    return ild_scores

def compute_ILD_by_condition(ild_scores, user_conditions):
    # Créer un dictionnaire : user_id -> condition_id
    user_condition_map = dict(zip(user_conditions['id'], user_conditions['condition_id']))

    # Grouper les ILD par condition
    condition_ilds = defaultdict(list)
    for user_id, ild in ild_scores.items():
        condition = user_condition_map.get(user_id)
        if condition is not None:
            condition_ilds[condition].append(ild)

    # Calcul des moyennes
    condition_ild_means = {
        condition: np.mean(scores) for condition, scores in condition_ilds.items()
    }

    return condition_ild_means

if __name__ == "__main__":
    predictions, similarity_matrix, user_conditions = load_data()
    print("\n=== Calcul de la diversité (ILD) sur top 5 produits par utilisateur ===")
    top_recommendations = group_top_predictions_by_user(predictions, top_n=5)
    ild_scores = compute_ILD_per_user(top_recommendations, similarity_matrix)

    # Affichage d’un échantillon
    for uid, ild in list(ild_scores.items())[:5]:
        print(f"User {uid} — ILD: {ild:.4f}")

    print(f"\nILD moyen sur tous les utilisateurs : {np.mean(list(ild_scores.values())):.4f}")
    print("\n=== ILD moyen par condition expérimentale ===")
    condition_ild_means = compute_ILD_by_condition(ild_scores, user_conditions)
    for condition, mean_ild in sorted(condition_ild_means.items()):
        print(f"Condition {condition} : ILD moyen = {mean_ild:.4f}")
