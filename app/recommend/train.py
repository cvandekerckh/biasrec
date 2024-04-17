from app.recommend.recsys import model
from app.recommend.loaders import load_ratings


def fit_model(ratings_file, model_name):
    sp_ratings = load_ratings(ratings_file)
    trainset = sp_ratings.build_full_trainset()
    anti_testset = trainset.build_anti_testset()
    assert model_name in model
    algo = model[model_name]()
    print('Start training...')
    algo.fit(trainset)
    print('Training ended with success !')
    return algo, anti_testset