import pickle
from collections import Counter, defaultdict
from config import Config as Cf
from app import create_app
from app.models import Product


# =================================================
# 🔧 Flask app context (obligatoire pour SQLAlchemy)
# =================================================
app = create_app()
app.app_context().push()


# =================================================
# 1️⃣ Charger les prédictions content-based (AVANT)
# =================================================
with open(
    Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / "predictions_05_05_2025.p",
    "rb"
) as f:
    predictions = pickle.load(f)


def get_topk_content_based(predictions, user_id, k):
    """
    Return Top-K (Product, score) for one user
    Predictions are NOT guaranteed to be sorted → explicit sort
    """
    user_preds = [
        (iid, est)
        for uid, iid, _, est, _ in predictions
        if str(uid) == str(user_id)
    ]

    user_preds.sort(key=lambda x: x[1], reverse=True)
    topk = user_preds[:k]

    return [
        (Product.query.get(pid), score)
        for pid, score in topk
        if Product.query.get(pid) is not None
    ]


# =================================================
# 2️⃣ Charger les recommandations multi-stakeholder
# =================================================
with open(Cf.DATA_PATH_OUT / "biased_recommendations_test_prolific.p", "rb") as f:
    recs = pickle.load(f)

print(f"\n📦 Nombre total d'utilisateurs : {len(recs)}\n")


# =================================================
# 3️⃣ Statistiques globales
# =================================================
condition_counter = Counter()
interaction_counter = Counter()
condition_interaction = defaultdict(Counter)

for user_id, data in recs.items():
    condition_id = data["condition_id"]
    n_interactions = data["n_interactions"]

    condition_counter[condition_id] += 1
    interaction_counter[n_interactions] += 1
    condition_interaction[condition_id][n_interactions] += 1


print("📊 Utilisateurs par condition :")
for cond in sorted(condition_counter):
    print(f"  Condition {cond}: {condition_counter[cond]}")

print("\n📊 Utilisateurs par nombre d'interactions :")
for n in sorted(interaction_counter):
    print(f"  {n} interaction(s): {interaction_counter[n]}")

print("\n📊 Détail condition × interactions :")
for cond in sorted(condition_interaction):
    print(
        f"  Condition {cond} → "
        + ", ".join(
            f"{n} interaction(s): {count}"
            for n, count in sorted(condition_interaction[cond].items())
        )
    )


# =================================================
# 4️⃣ Comparaison AVANT / APRÈS pour un utilisateur
# =================================================
USER_ID = list(recs.keys())[4]   # 🔁 change ici si besoin

print("\n" + "=" * 60)
print("🔍 INSPECTION UTILISATEUR :", USER_ID)
print("=" * 60)

user_data = recs[USER_ID]

print(f"Condition ID    : {user_data['condition_id']}")
print(f"N interactions  : {user_data['n_interactions']}")


# ---------- AVANT : content-based ----------
print("\n🟦 TOP-5 AVANT (Content-Based, non biaisé)")
top5_before = get_topk_content_based(
    predictions,
    USER_ID,
    Cf.N_RECOMMENDATIONS
)

for rank, (product, score) in enumerate(top5_before, start=1):
    print(
        f"  {rank}. {product.name} | "
        f"score={score:.2f} | "
        f"nutri={product.nutri_score}"
    )


# ---------- APRÈS : multi-stakeholder ----------
print("\n🟥 TOP-5 APRÈS (Multi-Stakeholder)")

for interaction_id, ranked_list in user_data["interactions"].items():
    print(f"\nInteraction {interaction_id}")
    for rank, (product, score, nutri_weight) in enumerate(
        ranked_list[:Cf.N_RECOMMENDATIONS],
        start=1
    ):
        print(
            f"  {rank}. {product.name} | "
            f"score={score:.2f} | "
            f"nutri={product.nutri_score} ({nutri_weight})"
        )
