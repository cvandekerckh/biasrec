import pickle
import pandas as pd
import numpy as np

from config import Config as Cf
from app import create_app
from app.models import Product

# ---------------------------------------------------------
# PARAMETERS
# ---------------------------------------------------------
N_RECOMMENDATIONS = Cf.N_RECOMMENDATIONS
ERROR_VALUE = 0.2
ERROR_TOL = 1e-6
SET_ID = 1  # condition 1 → interaction 1 → set 1

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

# Load evaluation table
df = pd.read_csv(
    Cf.DATA_PATH_OUT / "evaluation_multi_interaction.csv"
)

# Select users: condition 1 + error ≈ 0.2
debug_users = df[
    (df["condition_id"] == 1) &
    (np.isclose(df["error"], ERROR_VALUE, atol=ERROR_TOL))
]["user_id"].tolist()

print(f"\n{len(debug_users)} users in condition 1 with error ≈ 0.2")
print(debug_users)

# Load final (biased) recommendations
with open(
    Cf.DATA_PATH_OUT / "biased_recommendations_test_prolific_20_01_2026_final.p",
    "rb"
) as f:
    final_recommendations = pickle.load(f)

# Load original (content-based) predictions for set 1
with open(
    Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / "predictions_set1_prolific_final.pkl",
    "rb"
) as f:
    predictions_set1 = pickle.load(f)

# ---------------------------------------------------------
# HELPER: rebuild content-based ranking per user
# ---------------------------------------------------------
from collections import defaultdict
import random as rd

def get_ordered_items(predictions):
    rd.seed(0)
    ordered_items = defaultdict(list)
    for uid, iid, _, est, _ in predictions:
        ordered_items[str(uid)].append((int(iid), est))
    for uid in ordered_items:
        rd.shuffle(ordered_items[uid])
        ordered_items[uid].sort(key=lambda x: x[1], reverse=True)
    return ordered_items

ordered_items_set1 = get_ordered_items(predictions_set1)

# ---------------------------------------------------------
# DISPLAY RECOMMENDATIONS
# ---------------------------------------------------------

app = create_app()
with app.app_context():

    for u in debug_users:
        print("\n" + "=" * 60)
        print(f"USER {u}")

        # --- BEFORE (content-based) ---
        before_ids = [
            iid for iid, _ in ordered_items_set1[u][:N_RECOMMENDATIONS]
        ]

        before_products = [
            Product.query.filter_by(id=iid).first()
            for iid in before_ids
        ]

        print("\nBEFORE multi-stakeholder:")
        for p in before_products:
            print(f"- {p.id} | NutriScore: {p.nutri_score}")

        # --- AFTER (multi-stakeholder) ---
        after_list = final_recommendations[u]["interactions"][1]
        after_products = [p for p, _, _ in after_list[:N_RECOMMENDATIONS]]

        print("\nAFTER multi-stakeholder:")
        for p in after_products:
            print(f"- {p.id} | NutriScore: {p.nutri_score}")

        # --- SANITY CHECK ---
        same = before_ids == [p.id for p in after_products]
        print(f"\nSame ranking: {same}")
