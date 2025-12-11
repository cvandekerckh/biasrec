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
    POSTS_PER_PAGE = 9
    DATA_PATH = Path('data/fucam')
    DATA_PATH_RAW = DATA_PATH / 'raw'
    DATA_PATH_OUT = DATA_PATH / 'out'
    MODEL_PATH = DATA_PATH_OUT / 'versioning'/ '6_models'
    MODEL_FILENAME = 'model_05_05_2025.p'
    N_RECOMMENDATIONS = 5
    PROLIFIC_STUDY_ID = '688889840ef7e7483d59d667' #test

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
  'default'  :FixedRecommendationConfig,
}
