import sys
from pathlib import Path
import pickle
from collections import defaultdict

# ======================================================
# 1️⃣ Rendre l'app Flask importable
# ======================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app import create_app
from app.models import Product

# ======================================================
# 2️⃣ Initialiser le contexte Flask
# ======================================================
app = create_app()
app.app_context().push()

# ======================================================
# 3️⃣ Charger le fichier brut (all_predictions)
# ======================================================
input_path = Path(
    "data/prolific/out/recommendations_prolific.pkl"
)

with open(input_path, "rb") as f:
    all_predictions = pickle.load(f)

print("✅ File loaded")
print("Nb rows:", len(all_predictions))

# ======================================================
# 4️⃣ Reconstruction DU FORMAT FLASK
# ======================================================
product_list_per_user = defaultdict(list)
missing_products = set()

for user_id, product_id, _, score, _ in all_predictions:
    product = Product.query.get(product_id)

    if product is None:
        missing_products.add(product_id)
        continue

    product_list_per_user[user_id].append((product, score))

product_list_per_user = dict(product_list_per_user)

print("Nb users:", len(product_list_per_user))

# ======================================================
# 5️⃣ Sauvegarde (FORMAT IDENTIQUE À model_05_05_2025.p)
# ======================================================
output_path = Path(
    "data/prolific/out/versioning/6_models/model_prolific_flask_compatible.p"
)

with open(output_path, "wb") as f:
    pickle.dump(product_list_per_user, f)

print("✅ Flask-compatible model saved:", output_path)

if missing_products:
    print(f"⚠️ {len(missing_products)} product IDs missing")
