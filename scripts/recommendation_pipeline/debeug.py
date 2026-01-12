import pickle
from collections import Counter
from config import Config as Cf
from app import create_app
from app.models import Product

FILES = {
    "OLD": Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / "predictions_05_05_2025.p",
    "SET1": Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / "predictions_set1.pkl",
    "SET2": Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / "predictions_set2.pkl",
    "SET3": Cf.DATA_PATH_OUT / "versioning" / "4_predictions" / "predictions_set3.pkl",
}

app = create_app()

with app.app_context():
    for label, path in FILES.items():
        with open(path, "rb") as f:
            preds = pickle.load(f)

        product_ids = {iid for (_, iid, _, _, _) in preds}

        missing = [
            pid for pid in product_ids
            if Product.query.filter_by(id=pid).first() is None
        ]

        print(f"\n📦 {label}")
        print(f"Total product_ids : {len(product_ids)}")
        print(f"❌ Missing in DB  : {len(missing)}")

        if missing:
            print("Exemples :", missing[:10])
