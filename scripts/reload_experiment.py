import csv
import pandas as pd
from app import create_app
from flask import current_app
from app.models import User, Product
from app import db
from config import Config as Cf
from sqlalchemy import inspect
from sqlalchemy.exc import NoSuchTableError

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

    # print(table_names)
    # # Create a dictionary to store foreign key relationships
    # foreign_keys = {}

    # # Inspect foreign key constraints
    # inspector = inspect(db.engine)
    # for table_name in table_names:
    #     try:
    #         foreign_keys[table_name] = inspector.get_foreign_keys(table_name)
    #     except NoSuchTableError:
    #         continue

    # for key in foreign_keys:
    #     print(key)
    #     print([fk['referred_table'] for fk in foreign_keys[key]])
    #     print('\n')

    # # Drop tables in the correct order (from child to parent)
    # dropped_tables = set()
    # while len(dropped_tables) < len(table_names):
    #     for table_name in table_names:
    #         print(table_name)
    #         if table_name not in dropped_tables:
    #             if table_name in foreign_keys:
    #                 print('if')
    #                 dependent_tables = [fk['referred_table'] for fk in foreign_keys[table_name]]
    #                 print(dependent_tables)
    #                 if all(dep_table in dropped_tables for dep_table in dependent_tables):
    #                     print('drop')
    #                     metadata.tables[table_name].drop(db.engine)
    #                     dropped_tables.add(table_name)
    #             else:
    #                 print('else')
    #                 dropped_tables.add(table_name)

def reload_databases():
    with app.app_context():
        # Temporarily disable foreign key checks
        drop_all_tables()
        #db.session.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        #db.drop_all()
        # Re-enable foreign key checks
        #db.session.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        db.create_all()
        populate_products()
        populate_users()
        print('reloaded databases with success !')