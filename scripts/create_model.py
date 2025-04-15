import pandas as pd
from config import Config as Cf
from sklearn.metrics import pairwise_distances

INGREDIENT_COLUMNS = ["protein", "vegetables", "starches", "dairy_products", "sauce"]
PRODUCT_FILENAME = 'products.csv'
FEATMATRIX_FILENAME = 'featmatrix.csv'
SIMILARITY_MATRIX_FILENAME = 'similarity_matrix.csv'


def create_feature_matrix(
        product_path=Cf.DATA_PATH_RAW,
        product_filename=PRODUCT_FILENAME,
        featmatrix_path=Cf.DATA_PATH_OUT,
        featmatrix_filename=FEATMATRIX_FILENAME,
    ):
    # Charger le fichier CSV avec le bon séparateur
    df = pd.read_csv(product_path / product_filename, sep=";")
    
    # Liste des colonnes contenant les ingrédients
    ingredient_columns = ["protein", "vegetables", "starches", "dairy_products", "sauce"]
    
    # Extraire les ingrédients uniques
    unique_ingredients = set()
    for col in ingredient_columns:
        df[col] = df[col].fillna('')  # Remplir les valeurs manquantes par une chaîne vide
        for ingredients in df[col]:
            for ingredient in ingredients.split(" | "):
                ingredient = ingredient.strip()
                if ingredient.lower() != "no" and ingredient:  # Exclure "No" et les valeurs vides
                    unique_ingredients.add(ingredient)
    
    unique_ingredients = sorted(unique_ingredients)  # Trier les ingrédients pour avoir une ordre constant
    
    # Transformer la colonne catégorie en variables binaires avec 1/0
    categories = pd.get_dummies(df["category"], prefix="is").astype(int)
    
    # Créer une matrice vide avec l'ID du produit
    feature_matrix = pd.DataFrame(0, index=df.index, columns=["product_id"] + categories.columns.tolist() + unique_ingredients + ["nutri_score"])
    feature_matrix["product_id"] = df["id"]  # Ajouter l'ID du produit
    
    # Remplir la matrice avec les valeurs
    feature_matrix[categories.columns] = categories
    for col in ingredient_columns:
        for i, ingredients in enumerate(df[col]):
            for ingredient in ingredients.split(" | "):
                ingredient = ingredient.strip()
                if ingredient in feature_matrix.columns:
                    feature_matrix.at[i, ingredient] = 1
    
    # Convertir le nutri-score en valeurs numériques
    nutri_score_mapping = {"A": 1, "B": 0.75, "C": 0.50, "D": 0.25, "E": 0}
    feature_matrix["nutri_score"] = df["nutri_score"].map(nutri_score_mapping)

    # Renommer les colonnes liées aux ingrédients
    feature_matrix = feature_matrix.rename(columns = {ingredient : f'has_{ingredient}' for ingredient in unique_ingredients})
    feature_matrix = feature_matrix.set_index('product_id')

    # Sauvegarder dans un fichier CSV
    print('Saving feature matrix')
    feature_matrix.to_csv(featmatrix_path / featmatrix_filename)
    
    return feature_matrix


def create_similarity_matrix_with_metric(df, metric):
    distances = pairwise_distances(df.values, metric=metric)
    similarity = 1 - distances
    similarity_df = pd.DataFrame(similarity, 
                             index=df.index, 
                             columns=df.index)
    return similarity_df


def create_similarity_matrix(
        feature_matrix,
        weights=(0.25, 0.25, 0.50),
        similarity_matrix_path=Cf.DATA_PATH_OUT,
        similarity_matrix_filename=SIMILARITY_MATRIX_FILENAME,
    ):
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

def main():
    feature_matrix = create_feature_matrix()
    similarity_matrix = create_similarity_matrix(feature_matrix, weights=(0.25, 0.25, 0.50)) # first weight = category, second weight = nutriscore, third weight = ingredient

def train_model(user_trainset):
    pass

def make_prediction(user_testset):
    pass
