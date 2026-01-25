import pickle
import pandas as pd
from collections import defaultdict

from config import Config as Cf
from app import create_app
from app.models import Product


# =====================================================
# PARAMÈTRES
# =====================================================
TOP_K = Cf.N_RECOMMENDATIONS  # 5

NUTRI_MAP = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2,
    "E": 1,
}


# =====================================================
# LOAD CONTENT-BASED PREDICTIONS
# =====================================================
def load_predictions(set_id):
    filename = {
        1: "predictions_set1_25_01_2026.pkl",
        2: "predictions_set2_25_01_2026.pkl",
        3: "predictions_set3_25_01_2026.pkl",
    }[set_id]

    with open(
        Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / filename,
        "rb"
    ) as f:
        return pickle.load(f)


# =====================================================
# MAIN EXTRACTION FUNCTION
# =====================================================
def extract_user_level_content_based_vs_multistakeholder():
    app = create_app()
    rows = []

    with app.app_context():

        # -------------------------------------------------
        # CONTENT-BASED (UNBIASED)
        # -------------------------------------------------
        content_based = {}

        for set_id in [1, 2, 3]:
            preds = load_predictions(set_id)
            ordered = defaultdict(list)

            for uid, iid, _, est, _ in preds:
                ordered[str(uid)].append((iid, est))

            for uid in ordered:
                ordered[uid].sort(key=lambda x: x[1], reverse=True)
                content_based.setdefault(uid, {})[set_id] = ordered[uid][:TOP_K]

        # -------------------------------------------------
        # MULTI-STAKEHOLDER
        # -------------------------------------------------
        with open(
            Cf.DATA_PATH_OUT / "biased_recommendations_test_prolific_25_01_2026_final.p",
            "rb"
        ) as f:
            multistakeholder = pickle.load(f)

        # -------------------------------------------------
        # BUILD ROWS
        # -------------------------------------------------
        for user_id, user_data in multistakeholder.items():
            condition_id = int(user_data["condition_id"])

            # ===== CONTENT-BASED (UNBIASED)
            for interaction in [1, 2, 3]:
                for rank, (iid, _) in enumerate(
                    content_based[user_id][interaction],
                    start=1
                ):
                    product = Product.query.get(int(iid))
                    nutri_num = NUTRI_MAP[product.nutri_score]

                    rows.append({
                        "condition_id": condition_id,
                        "user_id": user_id,
                        "reco_type": "content_based_unbiased",
                        "interaction": interaction,
                        "rank": rank,
                        "product_id": product.id,
                        "product_name": product.name,
                        "nutri_score": product.nutri_score,
                        "nutri_score_numeric": nutri_num,
                    })

            # ===== MULTI-STAKEHOLDER
            for interaction, recs in user_data["interactions"].items():
                for rank, (product, _, _) in enumerate(recs[:TOP_K], start=1):
                    nutri_num = NUTRI_MAP[product.nutri_score]

                    rows.append({
                        "condition_id": condition_id,
                        "user_id": user_id,
                        "reco_type": "multistakeholder",
                        "interaction": interaction,
                        "rank": rank,
                        "product_id": product.id,
                        "product_name": product.name,
                        "nutri_score": product.nutri_score,
                        "nutri_score_numeric": nutri_num,
                    })

    # =====================================================
    # DATAFRAME
    # =====================================================
    df = pd.DataFrame(rows)

    # -----------------------------------------------------
    # FORCE ORDER OF RECO TYPE (KEY FIX)
    # -----------------------------------------------------
    df["reco_type"] = pd.Categorical(
        df["reco_type"],
        categories=[
            "content_based_unbiased",
            "multistakeholder",
        ],
        ordered=True,
    )

    # -----------------------------------------------------
    # MEAN NUTRISCORE TOP-5
    # -----------------------------------------------------
    mean_top5 = (
        df.groupby(
            ["condition_id", "user_id", "reco_type", "interaction"]
        )["nutri_score_numeric"]
        .mean()
        .reset_index()
        .rename(columns={"nutri_score_numeric": "mean_nutri_top5"})
    )

    df = df.merge(
        mean_top5,
        on=["condition_id", "user_id", "reco_type", "interaction"],
        how="left",
    )

    # -----------------------------------------------------
    # FINAL SORT (EXPERIMENTALLY CORRECT)
    # -----------------------------------------------------
    df = df.sort_values(
        by=[
            "condition_id",
            "user_id",
            "reco_type",
            "interaction",
            "rank",
        ]
    )

    return df


# =====================================================
# SCRIPT ENTRY POINT
# =====================================================
if __name__ == "__main__":
    df = extract_user_level_content_based_vs_multistakeholder()

    df.to_csv(
        Cf.DATA_PATH_OUT / "content_based_vs_multistakeholder_user_level_25_01_2026.csv",
        index=False,
    )

    print(df.head(30))
    print("Saved content_based_vs_multistakeholder_user_level_25_01_2026.csv")
