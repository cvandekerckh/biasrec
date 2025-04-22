from app.auth import bp
from flask import render_template, flash, redirect, url_for, current_app
from app.auth.forms import LoginForm, Close
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
    return redirect(url_for('auth.survey')) #redirige vers ma route survey

@bp.route('/closep2', methods=['GET', 'POST'])
@login_required
def closep2():
    return redirect(url_for('auth.surveyp2')) #redirige vers ma route survey

@bp.route('/survey', methods=['GET', 'POST'])
def survey():
    qualtrics_url = current_user.qualtrics_url
    logout_user()
    return render_template('main/survey.html', qualtrics_url=qualtrics_url) #redirige vers ma page survey

@bp.route('/surveyp2', methods=['GET', 'POST'])
def surveyp2():
    qualtrics_url = current_user.qualtrics_url
    logout_user()
    return render_template('main/surveyp2.html', qualtrics_url=qualtrics_url) #redirige vers ma page survey



