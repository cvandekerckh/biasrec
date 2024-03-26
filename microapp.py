import os
from app import create_app,db
from app.models import User, Product
from config import configs
from dotenv import load_dotenv
import argparse


parser = argparse.ArgumentParser(description='Purchases simulation for recommendation systems')
parser.add_argument('--config', type=str, default='default', help='Configuration name, see config.py')
args, _ = parser.parse_known_args()
config_name = args.config

app = create_app(config_class=configs[config_name])

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)