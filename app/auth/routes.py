from app.auth import bp
from flask import render_template, flash, redirect, url_for, current_app
from app.auth.forms import LoginForm, Close, LogoutForm
from flask_login import current_user, login_user, login_required, logout_user
import csv
from app.models import User


@bp.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('auth.login'))   


@bp.route('/login', methods=['GET', 'POST'])
def login(): #mettre le code de ce qu'il y a à faire sur cette page "login" = notre première page
    if current_user.is_authenticated:
        return redirect(url_for(current_app.config['MAIN_PAGE'])) #On redirige vers la page main
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(code=form.code.data).first()
        if user is None :
            flash('Invalid code')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for(current_app.config['MAIN_PAGE'])) #On redirige vers la page main 
    return render_template('auth/login.html', form=form)


@bp.route('/close', methods=['GET', 'POST'])
@login_required
def close():
    logout_user()
    return redirect(url_for('auth.survey2')) #redirige vers ma route survey2