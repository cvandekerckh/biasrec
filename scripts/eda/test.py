import sys
from pathlib import Path
import pickle

# ======================================================
# 1️⃣ Ajouter la racine du projet au PYTHONPATH
# ======================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# ======================================================
# 2️⃣ Imports Flask (obligatoires pour unpickle)
# ======================================================
from app import create_app
from app.models import Product

# ======================================================
# 3️⃣ Initialiser le contexte Flask
# ======================================================
app = create_app()
app.app_context().push()

# ======================================================
# 4️⃣ Charger le pickle
# ======================================================
path = Path(
    "data/prolific/out/versioning/6_models/model_05_05_2025.p"
)

with open(path, "rb") as f:
    data = pickle.load(f)

# ======================================================
# 5️⃣ Inspection
# ======================================================
print("Type:", type(data))
print("Nb users:", len(data))

u = list(data.keys())[0]
print("\nUser:", u)
print("First 3 recommendations:")
for product, score in data[u][:3]:
    print(f"- {product.name} (id={product.id}) | score={score}")


