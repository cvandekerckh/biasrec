import csv
from app import create_app
from flask import current_app
from app.models import User, Product, create_star_table
from app import db


app = create_app()

def delete_entries_from_db(db_name):
    entries = db_name.query.all()
    for entry in entries:
        db.session.delete(entry)
    db.session.commit()

def populate_db(db_name, csv_file):
    with open(csv_file, encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=";" )
        header = next(reader)
        for i in reader:
            kwargs = {column: value for column, value in zip(header, i)}
            new_entry = db_name(**kwargs)
            db.session.add(new_entry)
            db.session.commit()

def reload_databases():
    with app.app_context():
        delete_entries_from_db(User)
        delete_entries_from_db(Product)
        populate_db(User, "app/static/users.csv")
        populate_db(Product, "app/static/products.csv")
        create_star_table()
        print('reloaded databases with success !')