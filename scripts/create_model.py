import pandas as pd
from config import Config as Cf
from sklearn.metrics import pairwise_distances, mean_absolute_error, mean_squared_error
import json
import copy
import pickle 
from sklearn.model_selection import KFold
from sklearn.model_selection import GroupKFold
import numpy as np
import itertools

INGREDIENT_COLUMNS = ["protein", "vegetables", "starches", "dairy_products", "sauce"]
PRODUCT_FILENAME = 'products.csv'
FEATMATRIX_FILENAME = 'featmatrix.csv'
SIMILARITY_MATRIX_FILENAME = 'similarity_matrix.csv'
TRAINSET_FILENAME = 'rating_14_04_2025.csv'
USER_TEST_ID = 135

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
        feature_matrix,
        weights,
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

def get_full_trainset(
    trainset_path=Cf.DATA_PATH_RAW,
    trainset_filename=TRAINSET_FILENAME,
):
    df_train = pd.read_csv(trainset_path / trainset_filename, delimiter=';')
    df_train = df_train[(df_train['user_id'] != USER_TEST_ID)]
    return df_train

def get_full_testset(
        user_trainset,
        product_id_list
    ):

    # Preallocate model
    user_ids = user_trainset['user_id'].unique().tolist()
    testset = {user_id : {} for user_id in user_ids}

    for user_id in testset:
        # identify trainset products
        user_trainset_i = user_trainset[user_trainset['user_id'] == user_id].set_index('product_id')
        trainset_product_ids = user_trainset_i.index.tolist()
        # Identify testset products
        testset_product_ids = [
            product_id for product_id in product_id_list 
            if product_id not in trainset_product_ids
        ]
        testset[user_id] = {product_id : [] for product_id in testset_product_ids}
    return testset


def train_model(
        user_trainset, 
        product_id_list,
        similarity_matrix,
        k,
        model_path=Cf.DATA_PATH_OUT,
        model_filename='model.json'
    ):

    model = get_full_testset(user_trainset, product_id_list)

    print('Finding k nearest neighbours')
    for user_id in model:
        user_trainset_i = user_trainset[user_trainset['user_id'] == user_id].set_index('product_id')
        trainset_product_ids = user_trainset_i.index.tolist()
        for testset_product_id in model[user_id]:
            # get similarities
            similarities = similarity_matrix.loc[testset_product_id, similarity_matrix.columns.isin(trainset_product_ids)]

            # trier les k plus similaires
            k_closest_products = similarities.nlargest(k)

            # join ratings
            train_output = k_closest_products.to_frame('similarity').join(user_trainset_i['rating'])
            model[user_id][testset_product_id] = list(train_output.itertuples(index=True, name=None))

    # Dump to a JSON string
    model_string = json.dumps(model)
    with open(model_path / model_filename, 'w') as f:
        json.dump(model_string, f)

    return model


def predict_for_testset(
        testset,
        model,
        predictions_path=Cf.DATA_PATH_OUT,
        predictions_filename='predictions.p'
    ):
    predictions = []
    print('Aggregate ratings to make predictions')
    for user_id in testset:
        for product_id in testset[user_id]:
            # Extract similarities and ratings
            similarities, ratings = zip(*[
                (sim, rating) for _, sim, rating in model[user_id][product_id]
            ])
            numerator = sum(
                sim * rating 
                for sim, rating in zip(similarities, ratings)
            )
            denominator = sum(similarities)
            weighted_avg = numerator / denominator if denominator != 0 else 1
            predictions.append((user_id, product_id, None, weighted_avg, None))

    # Dump to a JSON string
    with open(predictions_path / predictions_filename, 'wb') as f:
        pickle.dump(predictions, f)

    return predictions

def evaluate_model_grid_search(
    ratings_df,
    feature_matrix,
    product_id_list,
    k_values,
    weight_combinations,
    k_folds=5,
    output_path=Cf.DATA_PATH_OUT,
    output_filename='evaluation_results.csv'
):
    results = []

    for weights in weight_combinations:
        print(f"\n--- Testing weights = {weights} ---")
        similarity_matrix = create_similarity_matrix(feature_matrix, weights=weights)

        for k in k_values:
            print(f"\n>> Testing k = {k}")
            mae_list, mse_list, rmse_list = [], [], []

            kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)
            for fold, (train_index, test_index) in enumerate(kf.split(ratings_df), 1):
                train_df = ratings_df.iloc[train_index]
                test_df = ratings_df.iloc[test_index]

                # Entraîner le modèle sur l'ensemble d'entraînement
                model = train_model(train_df, product_id_list, similarity_matrix, k=k)

                # Créer un testset au format attendu par predict_for_testset
                user_testset = {
                    uid: {pid: [] for pid in test_df[test_df['user_id'] == uid]['product_id'].tolist()}
                    for uid in test_df['user_id'].unique()
                }

                predictions = predict_for_testset(user_testset, model)

                y_true, y_pred = [], []
                for user_id, product_id, _, pred_rating, _ in predictions:
                    true_rating_row = test_df[(test_df['user_id'] == user_id) & (test_df['product_id'] == product_id)]
                    if not true_rating_row.empty:
                        true_rating = true_rating_row['rating'].values[0]
                        y_true.append(true_rating)
                        y_pred.append(pred_rating)

                if y_true:
                    mae = mean_absolute_error(y_true, y_pred)
                    mse = mean_squared_error(y_true, y_pred)
                    rmse = np.sqrt(mse)

                    mae_list.append(mae)
                    mse_list.append(mse)
                    rmse_list.append(rmse)

                print(f"Fold {fold} done – {len(y_true)} prédictions")

            if mae_list:
                mean_mae = np.mean(mae_list)
                mean_mse = np.mean(mse_list)
                mean_rmse = np.mean(rmse_list)

                print(f"Résultats pour k={k}, weights={weights}")
                print(f"MAE: {mean_mae:.4f}, RMSE: {mean_rmse:.4f}")

                results.append({
                    'model': 'content_based',
                    'k': k,
                    'weights': weights,
                    'mean_MAE': mean_mae,
                    'mean_MSE': mean_mse,
                    'mean_RMSE': mean_rmse
                })

    # Sauvegarder les résultats dans un CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path / output_filename, index=False)
    print(f"\n✅ Résultats enregistrés dans '{output_filename}'")

    return results

#Evaluation des systèmes de recommandation basés sur la moyenne des ratings, le random et le ratin le plus utilisé par le user (mode)
def evaluate_baseline_models(ratings_df, k_folds=5):
    results = []
    kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)

    for baseline in ['mean', 'random', 'mode']:
        print(f"\n--- Évaluation du modèle baseline : {baseline} ---")
        mae_list, mse_list, rmse_list = [], [], []

        for fold, (train_index, test_index) in enumerate(kf.split(ratings_df), 1):
            train_df = ratings_df.iloc[train_index]
            test_df = ratings_df.iloc[test_index]

            y_true, y_pred = [], []

            for user_id in test_df['user_id'].unique():
                user_train_ratings = train_df[train_df['user_id'] == user_id]['rating']
                user_test_data = test_df[test_df['user_id'] == user_id]

                if len(user_train_ratings) == 0:
                    continue  # skip si l'utilisateur n'a pas de données d'entraînement

                if baseline == 'mean':
                    pred_value = user_train_ratings.mean()
                elif baseline == 'mode':
                    pred_value = user_train_ratings.mode().iloc[0]
                elif baseline == 'random':
                    pred_value = np.random.choice(user_train_ratings.values)

                y_true.extend(user_test_data['rating'].tolist())
                y_pred.extend([pred_value] * len(user_test_data))

            if y_true:
                mae = mean_absolute_error(y_true, y_pred)
                mse = mean_squared_error(y_true, y_pred)
                rmse = np.sqrt(mse)
                mae_list.append(mae)
                mse_list.append(mse)
                rmse_list.append(rmse)

            print(f"Fold {fold} terminé – {len(y_true)} prédictions")

        results.append({
            'model': baseline,
            'mean_MAE': np.mean(mae_list),
            'mean_MSE': np.mean(mse_list),
            'mean_RMSE': np.mean(rmse_list)
        })

    return results

def generate_weight_combinations(step):
    """
    Génère toutes les combinaisons possibles de 3 poids (w1, w2, w3)
    tels que chaque poids est un multiple du pas (step)
    et que la somme des trois poids est exactement égale à 1.
    """
    decimals = len(str(step).split(".")[-1])  # pour gérer les arrondis
    values = [round(i * step, decimals) for i in range(int(1 / step) + 1)]
    all_combinations = itertools.product(values, repeat=3)
    valid_combinations = [
        combo for combo in all_combinations
        if round(sum(combo), decimals) == 1.0
    ]
    return valid_combinations

def main():
    feature_matrix = create_feature_matrix()
    similarity_matrix = create_similarity_matrix(feature_matrix, weights=(0.25, 0.25, 0.50)) # first weight = category, second weight = nutriscore, third weight = ingredient
    product_id_list = feature_matrix.index.tolist()
    user_trainset = get_full_trainset()
    user_testset = get_full_testset(user_trainset, product_id_list)
    model = train_model(user_trainset, product_id_list, similarity_matrix, k=5)
    #print(model[44849])
    predictions = predict_for_testset(user_testset, model)
    #print([prediction for prediction in predictions if prediction[0] == 44849])
    #print('predictions made with success')
    ratings_df = pd.read_csv(Cf.DATA_PATH_RAW / TRAINSET_FILENAME, delimiter=';')

    # Paramètres à tester
    k_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 36]
    weight_combinations = generate_weight_combinations(step=0.05)  # ou step=0.05 si tu veux plus de précision
    print(f"{len(weight_combinations)} combinaisons de poids générées.")
    # Lancer l’évaluation avec cross-validation
    results = evaluate_model_grid_search(
        ratings_df=ratings_df,
        feature_matrix=feature_matrix,
        product_id_list=product_id_list,
        k_values=k_values,
        weight_combinations=weight_combinations,
        k_folds=5
    )

    # Afficher les résultats
    print("\n--- Résumé global des performances ---")
    for res in results:
        print(f"k={res['k']}, weights={res['weights']} → MAE: {res['mean_MAE']:.4f}, RMSE: {res['mean_RMSE']:.4f}")

    # ⬇️ ⬇️ INSÈRE ICI le bloc suivant ⬇️ ⬇️
    # Sauvegarder dans un CSV (content-based uniquement)
    results_df = pd.DataFrame(results)
    results_df.to_csv(Cf.DATA_PATH_OUT / 'evaluation_results.csv', index=False)
    print("\n✅ Résultats enregistrés dans 'evaluation_results.csv'")

    # Baselines
    baseline_results = evaluate_baseline_models(ratings_df=ratings_df, k_folds=5)
    baseline_df = pd.DataFrame(baseline_results)
    baseline_df.to_csv(Cf.DATA_PATH_OUT / 'baseline_results.csv', index=False)
    print("\n✅ Résultats enregistrés dans 'baseline_results.csv'")

    # Fusionner les deux
    combined_results = results + baseline_results
    combined_df = pd.DataFrame(combined_results)
    combined_df.to_csv(Cf.DATA_PATH_OUT / 'all_models_evaluation.csv', index=False)
    print("\n✅ Tous les résultats enregistrés dans 'all_models_evaluation.csv'")

    # Afficher les 5 meilleurs modèles (selon MAE)
    print("\n🏆 Top 5 des modèles (MAE croissant) :")
    top5 = combined_df.sort_values(by='mean_MAE').head(5)
    print(top5[['model', 'k', 'weights', 'mean_MAE', 'mean_RMSE']])


    