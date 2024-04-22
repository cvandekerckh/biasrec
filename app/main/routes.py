from app.main import bp
from flask import render_template, flash, redirect, url_for, current_app, make_response, g
from flask_login import current_user, login_required, logout_user
from app.models import User, Product, Answers_survey1, Answers_survey2
from flask import request
from app.main.forms import PurchaseForm
from app.auth.forms import Close, LogoutForm
from app import db
from config import Config as Cf
import pickle
import csv
from scripts.train_recommender_model import create_recommender_model2


@bp.before_app_request
def before_request():
    if current_app.config['RECOMMENDATION'] == 'fixed':
        images = range(1, current_app.config['N_RECOMMENDATIONS']+1)
        g.reco_list = [Product.query.filter_by(image = str(image)).first() for image in images]
    elif current_app.config['RECOMMENDATION'] == 'trained':
        if current_user.is_authenticated:
            model_file = current_app.config['DATA_PATH'] / current_app.config['MODEL_FILENAME']
            product_list_per_user = pickle.load(open(model_file, 'rb'))
            n_recommendations = current_app.config['N_RECOMMENDATIONS']
            g.reco_list = product_list_per_user[current_user.id][:n_recommendations]
        else:
            g.reco_list = None
    elif current_app.config['RECOMMENDATION'] is None:
        g.reco_list = None

@bp.route('/recommendation')
@login_required
def recommendation():
    form = PurchaseForm()
    return render_template('main/recommendation.html', form = form, reco_list = g.reco_list)

@bp.route('/product_category/<category_name>')
@login_required
def product_category(category_name):
    if category_name == "sandw":
        products = Product.query.filter_by(feature_1 = "Sandw")
        category_name_label = "sandwiches"
    elif category_name == "salade":
        products = Product.query.filter_by(feature_1 = "Salad")
        category_name_label = "salades"

    page = request.args.get('page', 1, type = int)
    product_page = products.paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for(f'main.product_category', category_name=category_name, page=product_page.next_num) \
        if product_page.has_next else None
    prev_url = url_for(f'main.product_category', category_name=category_name, page=product_page.prev_num) \
        if product_page.has_prev else None
    return render_template('main/product_category.html', products=product_page.items, category_name_label=category_name_label, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/rate')
@login_required
def rate():
    initial_rating_value = 0
    query = current_user.assignments.select()
    products = db.session.scalars(query).all()
    ratings = [current_user.get_rating_for_product(product.id) for product in products]
    ratings = [rating if rating is not None else initial_rating_value for rating in ratings]
    return render_template("main/rate.html", ratings=ratings, products=products)

@bp.route("/save/", methods=["POST"])
def save():
  data = dict(request.form)
  current_user.add_rating(data["product_id"], data["stars"])
  return make_response("OK", 200)

@bp.route('/survey1', methods=['GET', 'POST'])
@login_required
def survey1():
    user_id = current_user.id
    # Train l'algo de recommandation
    # Récupérez les évaluations de l'utilisateur
    user_ratings = {}
    query = current_user.assignments.select()
    products = db.session.scalars(query).all()
    for product in products:
        user_ratings[product.id] = current_user.get_rating_for_product(product.id)
    print(user_ratings)
    # Ajout des ratings dans la table Rating
    for product_id, rating in user_ratings.items():
        current_user.add_rating(product_id, rating)
    # Ajout des ratings dans la base de données MovieLens (ratings.csv)
    ratings_file = Cf.DATA_PATH / 'ratings.csv'
    user_has_ratings = False
    with open(ratings_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['user_id']) == user_id:
                user_has_ratings = True
                break
    # Ajouter les notes uniquement si l'utilisateur n'a pas encore de notes enregistrées
    if not user_has_ratings:
        with open(ratings_file, 'a', newline='') as csvfile:
            fieldnames = ['user_id', 'product_id', 'rating']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Écrire les ratings dans le fichier CSV
            for product_id, rating in user_ratings.items():
                writer.writerow({'user_id': user_id, 'product_id': product_id, 'rating': rating})
    
    # Load_ratings, .fit, .test, MMR diversification
    recom = create_recommender_model2(user_id)
    print(recom)
    # Enregistrer les recommandations dans le fichier CSV
    recom_file = Cf.DATA_PATH / 'recom.csv'
    with open(recom_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        existing_recommendations_count = sum(1 for row in reader if row['user_id'] == str(user_id))
    # Ajouter de nouvelles recommandations uniquement si le nombre de recommandations pour l'utilisateur est inférieur à 10
    if existing_recommendations_count < 10:
        with open(recom_file, 'a', newline='') as csvfile:
            fieldnames = ['user_id', 'product_id', 'score_MMR']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            # Écrire les recommandations dans le fichier CSV
            for product_id, score_MMR in recom.items():
                writer.writerow({'user_id': user_id, 'product_id': product_id, 'score_MMR' : round(score_MMR,2)})
    
    # Redirige vers la première enquête
    return render_template('main/survey 1.html')

@bp.route('/recommendation2', methods=['GET', 'POST'])
@login_required
def recommendation2():
    existing_survey = Answers_survey1.query.filter_by(user_id=current_user.id).first()
    if existing_survey is None:
    # Aucune donnée existante pour cet utilisateur, donc nous ajoutons une nouvelle entrée
        # Récupérer les données du formulaire
        gender = request.form['gender']
        age = request.form['age']
        nationality = request.form['nationality']
        education = request.form['education']
        occupation = request.form['occupation']
        movie_watching_habits = request.form['movie-watching habits']
        movies_per_month = request.form['movies_per_month']
        preferred_genres = ', '.join(request.form.getlist('preferred_genres[]'))
        heard_of_rs = request.form['heard_of_rs']
        aware_of_rs = request.form['aware_of_rs']
        noticed_rs = request.form['noticed_rs']
        follow_recommendations = request.form['follow_recommendations']
        # Créer une nouvelle instance de Answers_survey1
        new_survey = Answers_survey1(
            user_id=current_user.id,
            gender=gender,
            age=age,
            nationality=nationality,
            education=education,
            occupation=occupation,
            movie_watching_habits=movie_watching_habits,
            movies_per_month=movies_per_month,
            preferred_genres=preferred_genres,
            heard_of_rs=heard_of_rs,
            aware_of_rs=aware_of_rs,
            noticed_rs=noticed_rs,
            follow_recommendations=follow_recommendations
        )
        # Ajouter l'instance à la session de la base de données
        db.session.add(new_survey)
        # Effectuer un commit pour enregistrer les modifications dans la base de données
        db.session.commit()

    form = PurchaseForm()
    recom_list = []

    # Récupérer les recommandations depuis le fichier recom.csv pour le current_user
    recom_file = Cf.DATA_PATH / 'recom.csv'
    with open(recom_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if row['user_id'] == str(current_user.id) :
                recom_list.append(row['product_id'])

    # Récupérer les informations sur les films recommandés depuis le fichier products.csv
    products_file = Cf.DATA_PATH / 'products.csv'
    recommended_movies = []
    with open(products_file, 'r', newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if row['id'] in recom_list:
                recommended_movies.append({
                    'name': row['name'],
                    'year': row['feature_1'],
                    'genres': row['feature_2'],
                    'actors': row['feature_3'],
                    'user_score': row['feature_4'],
                    'overview': row['nutri_score'],
                    'trailer_url': row['price'],
                    'image_url': row['image']
                })
    #print(recommended_movies)
    return render_template('main/_recommendation.html', form=form, recom_list=recommended_movies)


@bp.route('/survey2', methods=['GET', 'POST'])
def survey2():
    return render_template('main/survey 2.html') #redirige vers ma page survey2

@bp.route('/conclusion', methods=['GET', 'POST'])
@login_required
def conclusion():
    existing_survey2 = Answers_survey2.query.filter_by(user_id=current_user.id).first()
    if existing_survey2 is None:
    # Aucune donnée existante pour cet utilisateur, donc nous ajoutons une nouvelle entrée
        # Récupérer les données du formulaire
        Q1 = request.form['q1']
        Q2 = request.form['q2']
        Q3 = request.form['q3']
        Q4 = request.form['q4']
        Q5 = request.form['q5']
        Q6 = request.form['q6']
        Q7 = request.form['q7']
        Q8 = request.form['q8']
        Q9 = request.form['q9']
        Q10 = request.form['q10']
        Q11 = request.form['q11']
        Q12 = request.form['q12']
        Q13 = request.form['q13']
        Q14 = request.form['q14']
        Q15 = request.form['q15']
        Q16 = request.form['q16']
        # Créer une nouvelle instance de Answers_survey1
        new_survey2 = Answers_survey2(
            user_id=current_user.id,
            Q1=Q1,
            Q2=Q2,
            Q3=Q3,
            Q4=Q4,
            Q5=Q5,
            Q6=Q6,
            Q7=Q7,
            Q8=Q8,
            Q9=Q9,
            Q10=Q10,
            Q11=Q11,
            Q12=Q12,
            Q13=Q13,
            Q14=Q14,
            Q15=Q15,
            Q16=Q16
        )
        # Ajouter l'instance à la session de la base de données
        db.session.add(new_survey2)
        # Effectuer un commit pour enregistrer les modifications dans la base de données
        db.session.commit()

    logout_form = LogoutForm()
    return render_template('main/conclusion.html', logout_form=logout_form)  # Redirige vers la conclusion finale

@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect("https://app.prolific.com/submissions/complete?cc=C4ZWO20R")

@bp.route('/cart')
@login_required
def cart():
    form1 = PurchaseForm()
    form2 = Close()
    query = current_user.purchases.select()
    cart_products = db.session.scalars(query).all()
    print(cart_products)
    return render_template('main/cart.html', cart_products=cart_products, form1=form1, form2=form2)






@bp.route('/product/<name>')
@login_required
def product(name):
    product = Product.query.filter_by(name = name).first()
    form = PurchaseForm()
    return render_template('main/product_detail.html', product = product, form = form, reco_list = g.reco_list)

@bp.route('/purchase/<name>', methods=['POST'])
@login_required
def purchase(name):
    product = Product.query.filter_by(name=name).first()
    current_user.add_to_cart(product)
    db.session.commit()
    flash('Ton article {} a été rajouté au panier!'.format(name))
    return redirect(url_for('main.recommendation2'))

@bp.route('/unpurchase/<name>', methods=['POST'])
@login_required
def unpurchase(name):
    product = Product.query.filter_by(name=name).first()
    current_user.remove_from_cart(product)
    db.session.commit()
    flash('Ton article {} a été retiré de votre panier!'.format(name))
    return redirect(url_for('main.cart'))

