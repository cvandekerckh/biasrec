import os
from dotenv import load_dotenv
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    DATA_PATH=Path('app/static/data/test-recommender')
    MODEL_NAME='LatentFactorModel'
    MODEL_FILENAME = 'model.p'
    N_RECOMMENDATIONS = 3

class RateConfig(Config):
    MAIN_PAGE='main.rate'
    RECOMMENDATION=None

class FixedRecommendationConfig(Config):
    MAIN_PAGE='main.recommendation'
    RECOMMENDATION='fixed'

class TrainedRecommendationConfig(Config):
    MAIN_PAGE='main.recommendation' 
    RECOMMENDATION='trained' 


configs = {
  'rate'  : RateConfig,
  'fixedrec' : FixedRecommendationConfig,
  'trainrec' : TrainedRecommendationConfig,
  'default'  : RateConfig,
}