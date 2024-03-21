from app.auth import bp
from flask import render_template, flash, redirect, url_for
from app.auth.forms import LoginForm, Close
from flask_login import current_user, login_user, login_required, logout_user
import csv
from app import db
from app.models import User, Product, create_star_table


@bp.route('/', methods=['GET', 'POST'])
def run_csv():
    users = User.query.all()
    products = Product.query.all()
    for u in users : 
        db.session.delete(u)
    for p in products : 
        db.session.delete(p)
    db.session.commit()
    with open("users.csv", encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=";" )
        header = next(reader)
        for i in reader:
                kwargs = {column: value for column, value in zip(header, i)}
                new_entry = User(**kwargs)
                db.session.add(new_entry)
                db.session.commit()
    with open("products.csv", encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=";" )
        header = next(reader)
        for i in reader:
                kwargs = {column: value for column, value in zip(header, i)}
                new_entry = Product(**kwargs)
                db.session.add(new_entry)
                db.session.commit()
    create_star_table()
    return redirect(url_for('auth.login'))   


@bp.route('/login', methods=['GET', 'POST'])
def login(): #mettre le code de ce qu'il y a à faire sur cette page "login" = notre première page
    if current_user.is_authenticated:
        return redirect(url_for('main.main')) #On redirige vers la page main
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(code=form.code.data).first()
        if user is None :
            flash('Invalid code')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.main')) #On redirige vers la page main 
    return render_template('auth/login.html', form=form)

@bp.route('/close', methods=['GET', 'POST'])
@login_required
def close():
    logout_user()
    return redirect(url_for('auth.survey')) #redirige vers ma route survey

@bp.route('/survey', methods=['GET', 'POST'])
def survey():
    return render_template('main/survey.html') #redirige vers ma page survey



