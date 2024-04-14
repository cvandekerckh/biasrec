from flask import Flask, render_template, request, make_response
from flask_login import current_user
import pandas as pd
import sqlite3
import csv
from app.models import User, Product, Rating, Answers_survey2, Answers_survey1
from app import create_app
from app import db
from config import Config as Cf


app = create_app()


def display_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            #print(user)
            print(f"User: {user.id}")
            print(f"Code: {user.code}")
            print(f"Diversity factor: {user.diversity_factor}")
            print()

def display_ratings():
    with app.app_context():
        ratings = Rating.query.all()
        for rating in ratings:
            print(rating)


def get_mmr_score(user_id, product_id):
    recom_file = Cf.DATA_PATH / 'recom.csv'
    with open(recom_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if int(row['user_id']) == user_id and int(row['product_id']) == product_id:
                return float(row['score_MMR'])
            
def display_purchases():
    with app.app_context():
        for user in User.query.all():
            print(f"User: {user.id} (with code : {user.code})")
            print("------Purchased Products------")
            query = user.purchases.select()
            products = db.session.scalars(query).all()
            for product in products:
                mmr_score = get_mmr_score(user.id, product.id)
                print(f"- {product.id} - {product.name} - {mmr_score}")
            print()

def display_assignments():
    with app.app_context():
        for user in User.query.all():
            print(f"User {user.id} (with code : {user.code})")
            print("-------Assignments------")
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


def display_answers_survey1():
    with app.app_context():
        for user in User.query.all():
            print(f"User: {user.id} (with code : {user.code})")
            print("------Data survey 1------")
            query = user.answers_survey1.select()
            data = db.session.scalars(query).all()
            #print(data)
            for d in data:
                print(f"Gender : {d.gender}")
                print(f"Age : {d.age}")
                print(f"Nationality : {d.nationality}")
                print(f"Education : {d.education}")
                print(f"Occupation : {d.occupation}")
                print(f"Movies watching habits : {d.movie_watching_habits}")
                print(f"Movies per month : {d.movies_per_month}")
                print(f"Preferred genres : {d.preferred_genres}")
                print(f"Heard about RS : {d.heard_of_rs}")
                print(f"Aware of RS : {d.aware_of_rs}")
                print(f"Noticed RS : {d.noticed_rs}")
                print(f"Follow recommendations : {d.follow_recommendations}")
            print() 

def display_answers_survey2():
    with app.app_context():
        for user in User.query.all():
            print(f"User: {user.id} (with code : {user.code})")
            print("------Data survey 2------")
            query = user.answers_survey2.select()
            data = db.session.scalars(query).all()
            print(data)
            """for d in data:
                print(f"Q1 : {d.Q1}")
                print(f"Q2 : {d.Q2}")
                print(f"Q3 : {d.Q3}")
                print(f"Q4 : {d.Q4}")
                print(f"Q5 : {d.Q5}")
                print(f"Q6 : {d.Q6}")
                print(f"Q7 : {d.Q7}")
                print(f"Q8 : {d.Q8}")
                print(f"Q9 : {d.Q9}")
                print(f"Q10 : {d.Q10}")
                print(f"Q11 : {d.Q11}")
                print(f"Q12 : {d.Q12}")
                print(f"Q13 : {d.Q13}")
                print(f"Q14 : {d.Q14}")
                print(f"Q15 : {d.Q15}")
                print(f"Q16 : {d.Q16}")"""
            print() 

def export_data_to_csv():
    with app.app_context():
        data_user_file = Cf.DATA_PATH / 'user_data.csv'
        with open(data_user_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['User ID', 'User Code', 'Diversity Factor', 'Gender', 'Age', 'Nationality', 'Education', 'Occupation', 'Movies Watching Habits', 'Movies per Month', 'Preferred Genres', 'Heard About RS', 'Aware of RS', 'Noticed RS', 'Follow Recommendations', 'Purchases', 'Number of Purchases', 'MMR_score', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15', 'Q16'])

            users = User.query.all()
            for user in users:
                data_list = []
                #Base information
                user_id = user.id
                data_list.append(user_id)
                user_code = user.code
                data_list.append(user_code)
                user_diversity_factor = user.diversity_factor
                data_list.append(user_diversity_factor)

                #Survey 1 information
                query1 = user.answers_survey1.select()
                data1 = db.session.scalars(query1).all()
                for d in data1:
                    Gender = d.gender
                    data_list.append(Gender)
                    Age = d.age
                    data_list.append(Age)
                    Nationality = d.nationality
                    data_list.append(Nationality)
                    Education = d.education
                    data_list.append(Education)
                    Occupation = d.occupation
                    data_list.append(Occupation)
                    Movies_watching_habits = d.movie_watching_habits
                    data_list.append(Movies_watching_habits)
                    Movies_per_month = d.movies_per_month
                    data_list.append(Movies_per_month)
                    Preferred_genres = d.preferred_genres
                    data_list.append(Preferred_genres)
                    Heard_about_RS = d.heard_of_rs
                    data_list.append(Heard_about_RS)
                    Aware_of_RS = d.aware_of_rs
                    data_list.append(Aware_of_RS)
                    Noticed_RS = d.noticed_rs
                    data_list.append(Noticed_RS)
                    Follow_recommendations = d.follow_recommendations
                    data_list.append(Follow_recommendations)
                
                #Purchases information
                query = user.purchases.select()
                purchases = db.session.scalars(query).all()
                purchases_names = ', '.join([purchase.name for purchase in purchases])
                data_list.append(purchases_names)
                #data_list.append(purchases)    
                number_of_purchases = len(purchases)
                data_list.append(number_of_purchases)
                mmr_score = [get_mmr_score(user.id, product.id) for product in purchases]
                data_list.append(mmr_score)

                #Survey 2 information
                query2 = user.answers_survey2.select()
                data2 = db.session.scalars(query2).all()
                for d in data2:
                    Q1 = d.Q1
                    data_list.append(Q1)
                    Q2 = d.Q2
                    data_list.append(Q2)
                    Q3 = d.Q3
                    data_list.append(Q3)
                    Q4 = d.Q4
                    data_list.append(Q4)
                    Q5 = d.Q5
                    data_list.append(Q5)
                    Q6 = d.Q6
                    data_list.append(Q6)
                    Q7 = d.Q7
                    data_list.append(Q7)
                    Q8 = d.Q8
                    data_list.append(Q8)
                    Q9 = d.Q9
                    data_list.append(Q9)
                    Q10 = d.Q10
                    data_list.append(Q10)
                    Q11 = d.Q11
                    data_list.append(Q11)
                    Q12 = d.Q12
                    data_list.append(Q12)
                    Q13 = d.Q13
                    data_list.append(Q13)
                    Q14 = d.Q14
                    data_list.append(Q14)
                    Q15 = d.Q15
                    data_list.append(Q15)
                    Q16 = d.Q16
                    data_list.append(Q16)
            
                writer.writerow(data_list)