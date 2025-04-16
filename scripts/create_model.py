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

def find_k_nearest_rated_neighbors_from_matrix(
    similarity_matrix,
    product_path=Cf.DATA_PATH_RAW
    rated_products_file = ,
    k=5,
    sep=';',
    output_path=Cf.DATA_PATH_OUT,
    output_filename='top_k_neighbors.csv'
    ):
    # Charger les ids des produits notés
    rated_df = pd.read_csv(/rated_products_file, sep=sep)
    rated_ids = set(rated_df['product_id'].astype(str))

    # Tous les produits de la base
    all_product_ids = similarity_matrix.index.astype(str)
    
    # Identifier les produits non notés
    unrated_ids = [pid for pid in all_product_ids if pid not in rated_ids]

    results = []

    #parcourt la liste de tous kes produits non notés 
    for unrated_pid in unrated_ids:
        #pour chasue produit non noté 
        # Récupérer les similarités avec les produits notés uniquement
        similarities = similarity_matrix.loc[unrated_pid, similarity_matrix.columns.isin(rated_ids)]

        # Trier les k plus similaires
        top_k = similarities.nlargest(k)

        for neighbor_id, sim_score in top_k.items():
            results.append({
                'product_id': unrated_pid,
                'neighbor_id': neighbor_id,
                'similarity_score': sim_score
            })

    results_df = pd.DataFrame(results)

    # Sauvegarder dans un CSV
    if output_path is not None:
        output_file = output_path / output_filename
        print(f'Saving top-k neighbors to {output_file}')
        results_df.to_csv(output_file, index=False, sep=sep)

    return results_df

def main():
    feature_matrix = create_feature_matrix()
    similarity_matrix = create_similarity_matrix(feature_matrix, weights=(0.25, 0.25, 0.50)) # first weight = category, second weight = nutriscore, third weight = ingredient
    KNN = find_k_nearest_rated_neighbors_from_matrix(similarity_matrix)

def train_model(user_trainset, K):
    ### user_trainset = {id: rating}
    ### sortir pour chaque product_id qui n'est pas dans user_trainset une liste des K plus proche voisins 
    ### pour chaque produit, tu vas chercher les K plus proches voisins ayant un rating:  [(product_id, similarity_score)]
    ### traiter cas où on a pas K voisins


    # Lire un fichier avec les id du trainset 
    # A partir de la grosse matrice de similarité, pour chaque produit qui n'est pas dans le trainset, trouver les k plus proches voisins dans le trainset (sortir pour chacun : product_id / similarity score)

    pass

def make_prediction(user_testset):
    pass
