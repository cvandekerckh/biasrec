import csv
import pandas as pd
from app import create_app
from flask import current_app
from app.models import User, Product
from app import db
from config import Config as Cf

app = create_app()

# OUT
USER_FILENAME = 'users_conditions.csv'

# RAW
PRODUCT_FILENAME = 'products.csv'
ASSIGNMENTS_FILENAME = 'assignments.csv'

def delete_entries_from_db(db_name):
    entries = db_name.query.all()
    for entry in entries:
        db.session.delete(entry)
    db.session.commit()

def populate_db(db_name, csv_file):
    df = pd.read_csv(csv_file)
    for record in df.to_dict("records"):
        new_entry = db_name(**record)
        db.session.add(new_entry)
        db.session.commit()

def assign_products_to_users():
    df = pd.read_csv(Cf.DATA_PATH_RAW / ASSIGNMENTS_FILENAME)
    for user_id, product_id in zip(df['user_id'].values, df['product_id'].values):
        user = User.query.get(user_id.item())
        product = Product.query.get(product_id.item())
        if user and product:
            user.assign_product(product)
            db.session.commit()

def populate_users():
    populate_db(User, Cf.DATA_PATH_OUT / USER_FILENAME)
    assign_products_to_users()


def populate_products():
    populate_db(Product, Cf.DATA_PATH_RAW / PRODUCT_FILENAME)


def reload_databases():
    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_products()
        populate_users()
        print('reloaded databases with success !')