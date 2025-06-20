import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import Config as Cf

# Configuration des colonnes d'ingrédients
INGREDIENT_COLUMNS = ["protein", "vegetables", "starches", "dairy_products", "sauce"]


# Input fila
PRODUCT_FILENAME = 'products_ENG.csv'

# Fichier de sortie
FEATMATRIX_FILENAME = 'featmatrix.csv'

def create_feature_matrix(
    product_path=Cf.DATA_PATH_RAW,
    product_filename=PRODUCT_FILENAME,
    featmatrix_path=Cf.DATA_PATH_OUT,
    featmatrix_filename=FEATMATRIX_FILENAME,
):
    # Charger le fichier CSV avec le bon séparateur
    df = pd.read_csv(product_path / product_filename, sep=";")
    
    # Nettoyage des colonnes d'ingrédients
    unique_ingredients = set()
    for col in INGREDIENT_COLUMNS:
        df[col] = df[col].fillna('')
        for ingredients in df[col]:
            for ingredient in ingredients.split(" | "):
                ingredient = ingredient.strip()
                if ingredient.lower() != "no" and ingredient:
                    unique_ingredients.add(ingredient)
    unique_ingredients = sorted(unique_ingredients)

    # Nettoyer les valeurs de catégorie
    df["category"] = df["category"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)

    # Transformer en variables binaires
    categories = pd.get_dummies(df["category"], prefix="is").astype(int)

    # Initialiser la matrice
    feature_matrix = pd.DataFrame(0, index=df.index,
        columns=["product_id"] + categories.columns.tolist() + unique_ingredients + ["nutri_score"])
    feature_matrix["product_id"] = df["id"]
    feature_matrix[categories.columns] = categories

    # Remplir la matrice avec les ingrédients
    for col in INGREDIENT_COLUMNS:
        for i, ingredients in enumerate(df[col]):
            for ingredient in ingredients.split(" | "):
                ingredient = ingredient.strip()
                if ingredient in feature_matrix.columns:
                    feature_matrix.at[i, ingredient] = 1

    # Conversion pondérée du nutri-score
    nutri_score_mapping = {"A": 1, "B": 0.75, "C": 0.50, "D": 0.25, "E": 0}
    feature_matrix["nutri_score"] = df["nutri_score"].map(nutri_score_mapping)

    # Renommer les colonnes d'ingrédients
    feature_matrix = feature_matrix.rename(columns={ingredient: f"has_{ingredient}" for ingredient in unique_ingredients})
    feature_matrix = feature_matrix.set_index("product_id")

    # Sauvegarde
    print("Saving feature matrix...")
    feature_matrix.to_csv(featmatrix_path / featmatrix_filename)

    return feature_matrix

if __name__ == "__main__":
    featmatrix = create_feature_matrix()
