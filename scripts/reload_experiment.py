import csv
import pandas as pd
from app import create_app
from flask import current_app
from app.models import User, Product, Rating
from app import db
from config import Config as Cf
from sqlalchemy import inspect
from sqlalchemy.exc import NoSuchTableError

app = create_app()

USER_FILENAME = 'users.csv'
PRODUCT_FILENAME = 'products.csv'
RATING_FILEMAME = 'ratings.csv'
ASSIGNMENTS_FILENAME = 'assignments.csv'

def delete_entries_from_db(db_name):
    entries = db_name.query.all()
    for entry in entries:
        db.session.delete(entry)
    db.session.commit()

def populate_db(db_name, csv_file, delimiter = ';'):
    df = pd.read_csv(csv_file, delimiter=delimiter, encoding='latin1')
    for record in df.to_dict("records"):
        new_entry = db_name(**record)
        db.session.add(new_entry)
        db.session.commit()

def assign_products_to_users():
    df = pd.read_csv(Cf.DATA_PATH / ASSIGNMENTS_FILENAME, delimiter=';', encoding='latin1')
    for user_id, product_id in zip(df['user_id'].values, df['product_id'].values):
        user = User.query.get(user_id.item())
        product = Product.query.get(product_id.item())
        if user and product:
            user.assign_product(product)
            db.session.commit()

def populate_users():
    populate_db(User, Cf.DATA_PATH / USER_FILENAME)
    assign_products_to_users()


def populate_products():
    populate_db(Product, Cf.DATA_PATH / PRODUCT_FILENAME)


def populate_ratings():
    populate_db(Rating,Cf.DATA_PATH / RATING_FILEMAME, delimiter=',')


def drop_tables_in_order(table_names, foreign_keys, engine):
    # Function to perform topological sort
    def topological_sort(graph):
        visited = set()
        stack = []

        def dfs(node):
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
            stack.append(node)

        for node in graph.keys():
            if node not in visited:
                dfs(node)
        return stack

    # Create a graph of foreign key dependencies
    dependency_graph = {table: [] for table in table_names}
    for table, fks in foreign_keys.items():
        for fk in fks:
            dependency_graph[fk['referred_table']].append(table)

    # Perform topological sort to get the correct order of dropping tables
    sorted_tables = topological_sort(dependency_graph)
    print(sorted_tables)

    # Drop tables in the sorted order
    for table_name in sorted_tables:
        if inspect(db.engine).has_table(table_name):
            db.metadata.tables[table_name].drop(db.engine)
        #engine.execute(f"DROP TABLE IF EXISTS {table_name};")

def drop_all_tables():
    """Drop tables in correct order"""
    # Get metadata
    metadata = db.metadata

    # Get all table names
    table_names = metadata.tables.keys()
    print(table_names)

    # Create a dictionary to store foreign key relationships
    foreign_keys = {}
    inspector = inspect(db.engine)
    for table_name in table_names:
        try:
            foreign_keys[table_name] = inspector.get_foreign_keys(table_name)
        except NoSuchTableError:
            foreign_keys[table_name] = []

    drop_tables_in_order(table_names, foreign_keys, db.engine)

def reload_databases():
    with app.app_context():
        drop_all_tables()
        db.create_all()
        populate_products()
        populate_users()
        populate_ratings()
        print('reloaded databases with success !')