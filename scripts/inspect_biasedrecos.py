# inspect_biased_recommendations.py

import pickle
from config import Config as Cf
from app import create_app

app = create_app()

with app.app_context():
    with open(Cf.DATA_PATH_OUT / "biased_recommendations.p", "rb") as f:
        data = pickle.load(f)

    print("Type:", type(data))
    print("Nombre d'utilisateurs:", len(data))

    # Inspecter un utilisateur
    user_id = list(data.keys())[0]
    print("\nUser ID:", user_id)
    print("Keys:", data[user_id].keys())

    rec = data[user_id]
    print("Eligible:", rec["eligible"])
    print("Delta (condition):", rec["bias_category"])
    print("Erreur:", rec["error"])

    print("\nTop-5 recommandations:")
    for p, score, nutri in rec["recommendation_list"][:5]:
        print(
            f"- Product ID={p.id}, Nutri={p.nutri_score}, "
            f"Weight={nutri}, Score={score:.3f}"
        )
