import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import Config as Cf
from sklearn.metrics import pairwise_distances

# Configuration des colonnes d'ingrédients
INGREDIENT_COLUMNS = ["protein", "vegetables", "starches", "dairy_products", "sauce"]


# Input fila
PRODUCT_FILENAME = 'products_ENG.csv'

# Fichier de sortie
FEATMATRIX_FILENAME = 'featmatrix_ok.csv'

# Optimal values
OPTIMAL_WEIGHTS = (0.1, 0.2, 0.7) # first weight = category, second weight = nutriscore, third weight = ingredient
OPTIMAL_WEIGHTS_BIS = (1, 0, 0) # focus on category
OPTIMAL_K = 4

# Output files
FEATMATRIX_FILENAME = 'featmatrix_ok.csv'
SIMILARITY_MATRIX_PATH = Cf.DATA_PATH_OUT
SIMILARITY_MATRIX_FILENAME = f'similarity_matrix_20_06_2025_fcat.csv'

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

def create_similarity_matrix_with_metric(df, metric):
    X = df.values
    if metric == 'jaccard':
        X = X.astype(bool)
    distances = pairwise_distances(X, metric=metric)
    similarity = 1 - distances
    similarity_df = pd.DataFrame(similarity,
                             index=df.index,
                             columns=df.index)
    return similarity_df


def create_similarity_matrix(
        weights=OPTIMAL_WEIGHTS_BIS,
        similarity_matrix_path=SIMILARITY_MATRIX_PATH,
        similarity_matrix_filename=SIMILARITY_MATRIX_FILENAME,
    ):
    feature_matrix = create_feature_matrix()

    # Step 1 : create three similarity matrices
    # 1.1 - Similarity matrix based on product categories
    category_cols = [col for col in feature_matrix.columns if col.startswith('is_')]
    category_df = feature_matrix[category_cols]
    category_similarity_matrix = create_similarity_matrix_with_metric(category_df,'jaccard')

    # Optional: display or save the similarity matrix
    # 1.2 - Similarity matrix based on nutriscore
    nutriscore_cols = ['nutri_score']
    nutriscore_df = feature_matrix[nutriscore_cols]
    nutriscore_similarity_matrix = create_similarity_matrix_with_metric(nutriscore_df,'manhattan')

    # 1.3 - Similarity matrix based on ingredients
    ingredient_cols = [col for col in feature_matrix.columns if col.startswith('has_')]
    ingredient_df = feature_matrix[ingredient_cols]
    ingredient_similarity_matrix = create_similarity_matrix_with_metric(ingredient_df, 'jaccard')

    similarity_matrix = weights[0]*category_similarity_matrix + weights[1]*nutriscore_similarity_matrix + weights[2]*ingredient_similarity_matrix
    # Save in csv file
    print('Saving similarity matrix')
    similarity_matrix.to_csv(similarity_matrix_path / similarity_matrix_filename)

    return similarity_matrix

if __name__ == "__main__":
    create_similarity_matrix()
