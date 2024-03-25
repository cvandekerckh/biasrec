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
    DATA_PATH=Path('app/static/data/test-flask')

class RateConfig(Config):
    MAIN_PAGE='main.rate'

class RecommendConfig(Config):
    MAIN_PAGE='main.main'


configs = {
  'rate'  : RateConfig,
  'recommend' : RecommendConfig,
  'default'  : RateConfig,
}