import pickle
from pathlib import Path
from collections import defaultdict
import pandas as pd

def load_predictions(pickle_path):
    with open(pickle_path, "rb") as f:
        predictions = pickle.load(f)
    return predictions

def group_top_recommendations(predictions, top_n=5):
    user_recommendations = defaultdict(list)
    for user_id, product_id, _, rating, _ in predictions:
        user_recommendations[user_id].append((product_id, rating))

    top_recommendations = {
        user_id: [str(pid) for pid, _ in sorted(items, key=lambda x: x[1], reverse=True)[:top_n]]
        for user_id, items in user_recommendations.items()
    }
    return top_recommendations

def save_recommendations_to_csv(recommendations, output_file):
    data = [{'login': user_id, 'recommendations': ','.join(recos)} for user_id, recos in recommendations.items()]
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"✅ Recommandations exportées dans : {output_file}")

if __name__ == "__main__":
    # === Chemin vers le fichier pickle de prédictions ===
    recommendation_file = Path("C:/Users/camcharles/OneDrive - UCL/Documents/code/biasrec/data/fucam/out/versioning/predictions/predictions_05_05_2025.p")
    output_csv = Path("C:/Users/camcharles/OneDrive - UCL/Documents/code/biasrec/data/fucam/out/top5_recommendations_by_user.csv")

    predictions = load_predictions(recommendation_file)
    top_recommendations = group_top_recommendations(predictions, top_n=5)
    save_recommendations_to_csv(top_recommendations, output_csv)
