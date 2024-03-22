from flask import Flask, render_template, request, make_response
import pandas as pd
import sqlite3
import csv
from app.models import User, Product
from app import create_app
from app import db


DBFILE = "stars.db"

app = create_app()


def display_user_ratings():
    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect(DBFILE)
    df = pd.read_sql_query("SELECT * FROM `star_rating`", con)

    # Verify that result of SQL query is stored in the dataframe
    print(df)

    con.close()


def display_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(user)
            print(user.id)

def display_purchases():
    with app.app_context():
        for user in User.query.all():
            print(f"User: {user.code}")
            print("Purchased Products:")
            query = user.bought_products.select()
            products = db.session.scalars(query).all()
            for product in products:
                print(f"- {product.name}")
            print()

def display_products():
    with app.app_context():
        products = Product.query.all()
        for product in products:
            print(product)