from flask import Flask, render_template, request, make_response
import pandas as pd
import sqlite3
import csv
from app.models import User, Product
from app import create_app


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


def display_products():
    with app.app_context():
        products = Product.query.all()
        for product in products:
            print(product)