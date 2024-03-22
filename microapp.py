import os
from app import create_app,db
from app.models import User, Product
from config import configs
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
experiment_config = os.environ.get('EXPERIMENT_CONFIG') or 'default'
app = create_app(config_class=configs[experiment_config])


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)