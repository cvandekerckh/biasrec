from flask import Flask, render_template, request, make_response
import pandas as pd
import sqlite3
import csv
from app.models import User, Product, Rating
from app import create_app
from app import db


app = create_app()


def display_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(user)

def display_ratings():
    with app.app_context():
        ratings = Rating.query.all()
        for rating in ratings:
            print(rating)

def display_purchases():
    with app.app_context():
        for user in User.query.all():
            print(f"User: {user.code}")
            print("Purchased Products:")
            query = user.purchases.select()
            products = db.session.scalars(query).all()
            for product in products:
                print(f"- {product.name}")
            print()

def display_assignments():
    with app.app_context():
        for user in User.query.all():
            print(f"User: {user.code}")
            print("Assignments:")
            query = user.assignments.select()
            products = db.session.scalars(query).all()
            for product in products:
                print(f"- {product.name}")
            print()

def display_products():
    with app.app_context():
        products = Product.query.all()
        for product in products:
            print(product)
