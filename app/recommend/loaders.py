import pandas as pd
from surprise import Dataset
from surprise import Reader


def load_ratings(ratings_file):
    df_ratings = pd.read_csv(ratings_file)
    reader = Reader(rating_scale=(0.5,5))
    ratings_dataset = Dataset.load_from_df(df_ratings, reader)
    return ratings_dataset
