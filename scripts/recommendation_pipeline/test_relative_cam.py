import pickle
from collections import Counter, defaultdict
from config import Config as Cf
from app import create_app
from app.models import Product
from collections import defaultdict
import random as rd


# =================================================
# 🔧 Flask app context
# =================================================
app = create_app()
app.app_context().push()


# =================================================
# 1️⃣ Charger les prédictions content-based (par set)
# =================================================
PREDICTIONS_FILES = {
    1: "predictions_set1.pkl",
    2: "predictions_set2.pkl",
    3: "predictions_set3.pkl",
}

def normalize_user_ids_to_str(d):
    return {str(k): v for k, v in d.items()}


def get_ordered_items(predictions):
    rd.seed(0)
    ordered_items = defaultdict(list)
    for uid, iid, _, est, _ in predictions:
        ordered_items[str(uid)].append((iid, est))

    for uid in ordered_items:
        ordered_items[uid].sort(key=lambda x: x[1], reverse=True)

    return ordered_items


def get_product_list(ordered_items):
    product_list_per_user = {}
    for uid, items in ordered_items.items():
        plist = []
        for pid, score in items:
            product = Product.query.get(int(pid))
            if product is not None:
                plist.append((product, score, None))  # weight inutile AVANT
        product_list_per_user[uid] = plist
    return product_list_per_user


product_lists_per_set = {}

for set_id, filename in PREDICTIONS_FILES.items():
    with open(
        Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / filename,
        "rb"
    ) as f:
        predictions = pickle.load(f)

    ordered_items = get_ordered_items(predictions)
    product_lists_per_set[set_id] = normalize_user_ids_to_str(
        get_product_list(ordered_items)
    )


# =================================================
# 2️⃣ Charger les recommandations multi-stakeholder
# =================================================
with open(
    Cf.DATA_PATH_OUT / "biased_recommendations_test_prolific_final.p",
    "rb"
) as f:
    recs = pickle.load(f)

print(f"\n📦 Nombre total d'utilisateurs : {len(recs)}\n")


# =================================================
# 3️⃣ Comparaison AVANT / APRÈS
# =================================================
USER_ID = list(recs.keys())[6]

print("\n" + "=" * 90)
print("🔍 INSPECTION UTILISATEUR :", USER_ID)
print("=" * 90)

user_data = recs[USER_ID]

print(f"Condition ID    : {user_data['condition_id']}")
print(f"N interactions  : {user_data['n_interactions']}")

for interaction_id, ranked_list_after in user_data["interactions"].items():

    print("\n" + "-" * 90)
    print(f"🔄 INTERACTION {interaction_id}")
    print("-" * 90)

    # ---------- AVANT ----------
    print("\n🟦 AVANT — Content-Based PUR")

    topk_before = product_lists_per_set[interaction_id][USER_ID][:Cf.N_RECOMMENDATIONS]

    for rank, (product, score, _) in enumerate(topk_before, start=1):
        print(
            f"  {rank}. {product.name} | "
            f"  id= {product.id} | "
            f"score={score:.2f} | "
            f"nutri={product.nutri_score}"
        )

    # ---------- APRÈS ----------
    print("\n🟥 APRÈS — Multi-Stakeholder")

    for rank, (product, score, weight) in enumerate(
        ranked_list_after[:Cf.N_RECOMMENDATIONS],
        start=1
    ):
        print(
            f"  {rank}. {product.name} | "
            f"score={score:.2f} | "
            f"nutri={product.nutri_score} "
            f"(weight={weight})"
        )
