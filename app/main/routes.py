from app.main import bp
from flask import render_template, flash, redirect, url_for, current_app, make_response, g
from flask import session
from flask_login import current_user, login_required
from app.models import User, Product, Rating
from flask import request
from app.main.forms import PurchaseForm
from app.auth.forms import Close
from app import db
import pickle
import random
import hashlib
from app.models import PurchaseLog




category_tag_to_name = {
    'Poultry': 'Poultry',
    'Red meat': 'Red meat',
    'Fish': 'Fish',
    'Shellfish': 'Shellfish',
    'Vegetarian': 'Vegetarian',
}

def get_n_product_in_cart():
    query = current_user.purchases.select()
    cart_products = db.session.scalars(query).all()
    return len(cart_products)

@bp.before_app_request
def before_request():
    g.user_recs = None
    if current_app.config['RECOMMENDATION'] == 'fixed':
        ids = range(1, current_app.config['N_RECOMMENDATIONS'] + 1)
        g.reco_list = [Product.query.filter_by(id=id).first() for id in ids]

    elif current_app.config['RECOMMENDATION'] == 'trained':
        if current_user.is_authenticated:

            model_file = current_app.config['MODEL_PATH'] / current_app.config['MODEL_FILENAME']
            recs = pickle.load(open(model_file, "rb"))
            # 🔍 DEBUG — TEMPORAIRE
            print("🔍 DEBUG FLASK RECOMMENDATION")
            print("current_user.id =", current_user.id)
            print("current_user.code (str) =", str(current_user.code))
            print("First keys in pickle =", list(recs.keys())[:5])
            print("User in pickle =", str(current_user.code) in recs)
            print("-" * 50)

            user_recs = recs.get(str(current_user.code))

            if user_recs is None:
                g.reco_list = None
                return

            g.user_recs = user_recs

            # 🔹 interaction courante (0,1,2) → (1,2,3)
            interaction_idx = session.get("interaction_count", 0) + 1

            # 🔹 sécurité : ne pas dépasser le nombre d’interactions prévues
            if interaction_idx > user_recs["n_interactions"]:
                g.reco_list = None
                return

            # 🔹 liste complète re-rankée pour cette interaction
            full_ranked_list = user_recs["interactions"][interaction_idx]

            # 🔹 Top-5
            top_k = full_ranked_list[:current_app.config['N_RECOMMENDATIONS']]

            # 🔹 Flask attend juste des Product
            g.reco_list = [product for product, _, _ in top_k]

        else:
            g.reco_list = None

    elif current_app.config['RECOMMENDATION'] is None:
        g.reco_list = None


@bp.route('/recommendation')
@login_required
def recommendation():
    form = PurchaseForm()
    n_product_in_cart = get_n_product_in_cart()
    return render_template(
        'main/recommendation.html',
        form = form,
        reco_list = g.reco_list, 
        n_product_in_cart = n_product_in_cart,
    )

@bp.route('/product_category/<category_name>')
@login_required
def product_category(category_name):

    form = PurchaseForm()
    category_name_label = category_tag_to_name[category_name]

    # 1️⃣ Récupération
    products = Product.query.filter_by(category=category_name_label).all()

    # 2️⃣ Mélange déterministe
    def deterministic_key(product):
        key = f"{category_name}_{product.id}"
        return hashlib.md5(key.encode()).hexdigest()

    products = sorted(products, key=deterministic_key)

    # 3️⃣ Pagination
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    start = (page - 1) * per_page
    end = start + per_page
    product_items = products[start:end]

    next_url = url_for('main.product_category', category_name=category_name, page=page + 1) \
        if end < len(products) else None
    prev_url = url_for('main.product_category', category_name=category_name, page=page - 1) \
        if page > 1 else None

    n_product_in_cart = get_n_product_in_cart()

    return render_template(
        'main/product_category.html',
        products=product_items,
        category_name_label=category_name_label,
        next_url=next_url,
        prev_url=prev_url,
        form=form,
        n_product_in_cart=n_product_in_cart
    )


@bp.route('/rate')
@login_required
def rate():
    #qualtrics_url = current_user.qualtrics_url #chercher le lien url personnalisé vers le questionnaire Qualtrics Q2
    qualtrics_url = "https://lourim.eu.qualtrics.com/jfe/form/SV_bOYhP75UcU0Lyei"
    initial_rating_value = 0
    #all_products = Product.query.all()
    query = current_user.assignments.select()
    #products = db.session.scalars(query).all()
    all_products = db.session.scalars(query).all()
    all_products_dict = {p.id: p for p in all_products}

    # Garde l’ordre aléatoire une seule fois par session
    if ('product_order' not in session or len(session['product_order']) != len(all_products)):
        product_ids = [p.id for p in all_products]

        rng = random.Random(hash(current_user.code))  # 🔵 AJOUT
        rng.shuffle(product_ids)                      # 🔵 REMPLACE random.shuffle

        session['product_order'] = product_ids[:40]   # 🔴 INCHANGÉ
        
    ids = session['product_order']
    products = [all_products_dict[pid] for pid in ids if pid in all_products_dict]

    # Notes de l'utilisateur
    ratings = [current_user.get_rating_for_product(p.id) for p in products]
    ratings = [r if r is not None else initial_rating_value for r in ratings]

    # Produits non encore notés
    ratings_dict = {
        r.product_id: r.rating for r in db.session.scalars(
            db.select(Rating).filter(Rating.user_id == current_user.id)
        )
    }
    unrated_products = [p for p in products if p.id not in ratings_dict]

    return render_template("main/rate.html", ratings=ratings, products=products, unrated_products=unrated_products, qualtrics_url=qualtrics_url)

@bp.route("/save/", methods=["POST"])
def save():
  data = dict(request.form)
  current_user.add_rating(data["product_id"], data["stars"])
  return make_response("OK", 200)


@bp.route('/product/<name>')
@login_required
def product(name):
    product = Product.query.filter_by(name = name).first()
    form = PurchaseForm()
    n_product_in_cart = get_n_product_in_cart()
    return render_template('main/product_detail.html', product = product, form = form, reco_list = g.reco_list, n_product_in_cart = n_product_in_cart)

@bp.route('/cart')
@login_required
def cart():
    form1 = PurchaseForm()
    form2 = Close()
    query = current_user.purchases.select()
    cart_products = db.session.scalars(query).all()
    return render_template(
        'main/cart.html',
        cart_products = cart_products,
        form1 = form1,
        form2 = form2,
        n_product_in_cart=len(cart_products),
    )

@bp.route('/intermediate', methods=['GET'])
@login_required
def intermediate():
    return render_template('main/intermediate.html')

@bp.route('/validate_interaction', methods=['POST'])
@login_required
def validate_interaction():

    query = current_user.purchases.select()
    cart_products = db.session.scalars(query).all()

    interaction_count = session.get("interaction_count", 0)

    user_recs = g.user_recs
    if user_recs is None:
        # Sécurité prod : éviter un crash
        print("ERROR: user_recs is None for user", current_user.code)
        return redirect(url_for('main.recommendation'))
        
    condition_id = user_recs["condition_id"]
    n_interactions = user_recs["n_interactions"]

    # 🔹 LOG DB (safe GCloud)
    for product in cart_products:
        log = PurchaseLog(
            user_id=current_user.id,
            product_id=product.id,
            interaction=interaction_count,
            condition_id=condition_id
        )
        db.session.add(log)

    # 🔹 vider le panier
    for product in cart_products:
        current_user.remove_from_cart(product)

    db.session.commit()

    # 🔹 incrément après validation
    session["interaction_count"] = interaction_count + 1

    if session["interaction_count"] >= n_interactions:
        return redirect(url_for('auth.surveyp2'))

    return redirect(url_for('main.intermediate'))



@bp.route('/reminderreco', methods=['GET', 'POST'])
@login_required
def reminderreco():
    form = PurchaseForm()
    return render_template('main/reminder_recos.html', reco_list=g.reco_list, form=form)

@bp.route('/purchase/<name>', methods=['POST'])
@login_required
def purchase(name):
    product = Product.query.filter_by(name=name).first()
    current_user.add_to_cart(product)
    db.session.commit()
    flash('Ton article {} a été rajouté au panier!'.format(name))
    return redirect(url_for('main.product', name=name))

@bp.route('/purchasereco/<name>', methods=['POST'])
@login_required
def purchasereco(name):
    product = Product.query.filter_by(name=name).first()
    current_user.add_to_cart(product)
    db.session.commit()
    flash('Ton article {} a été rajouté au panier!'.format(name))
    return redirect(url_for('main.recommendation'))

@bp.route('/unpurchasecart/<name>', methods=['POST'])
@login_required
def unpurchasecart(name):
    product = Product.query.filter_by(name=name).first()
    current_user.remove_from_cart(product)
    db.session.commit()
    flash('Ton article {} a été retiré de votre panier!'.format(name))
    return redirect(url_for('main.cart'))

@bp.route('/unpurchasereco/<name>', methods=['POST'])
@login_required
def unpurchasereco(name):
    product = Product.query.filter_by(name=name).first()
    current_user.remove_from_cart(product)
    db.session.commit()
    flash('Ton article {} a été retiré de votre panier!'.format(name))
    return redirect(url_for('main.recommendation'))

@bp.route('/unpurchaseproduct/<name>', methods=['POST'])
@login_required
def unpurchaseproduct(name):
    product = Product.query.filter_by(name=name).first()
    current_user.remove_from_cart(product)
    db.session.commit()
    flash('Ton article {} a été retiré de votre panier!'.format(name))
    return redirect(url_for('main.product', name=name))
