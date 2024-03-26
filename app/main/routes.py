from app.main import bp
from flask import render_template, flash, redirect, url_for, current_app, make_response, g
from flask_login import current_user, login_required
from app.models import User, Product
from flask import request
from app.main.forms import PurchaseForm
from app.auth.forms import Close
from app import db
import pickle


@bp.before_app_request
def before_request():
    model_file = current_app.config['DATA_PATH'] / current_app.config['MODEL_FILENAME']
    product_list_per_user = pickle.load(open(model_file, 'rb'))
    n_recommendations = current_app.config['N_RECOMMENDATIONS']
    g.reco_list = product_list_per_user[current_user.id][:n_recommendations]


@bp.route('/recommendation')
@login_required
def recommendation():
    if current_app.config['RECOMMENDATION'] == 'fixed':
        images = range(1, current_app.config['N_RECOMMENDATIONS']+1)
        reco_list = [Product.query.filter_by(image = str(image)).first() for image in images]

    elif current_app.config['RECOMMENDATION'] == 'trained':
        reco_list = g.reco_list
        
    form = PurchaseForm()
    return render_template('main/recommendation.html', form = form, reco_list = reco_list)

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

    query = current_user.assignments.select()
    products = db.session.scalars(query).all()
    produit1 = products[0]
    produit2 = products[1]

    ustar = current_user.get_rating_for_product(products[0].id)
    if ustar is None : 
        ustar = 3

    ustarbis = current_user.get_rating_for_product(products[1].id)
    if ustarbis is None : 
        ustarbis = 3

    return render_template("main/rate.html", ustar=ustar, ustarbis=ustarbis, produit1 = produit1, produit2 = produit2)

@bp.route("/save/", methods=["POST"])
def save():
  data = dict(request.form)
  current_user.add_rating(data["product_id"], data["stars"])
  return make_response("OK", 200)


@bp.route('/product/<name>')
@login_required
def product(name):
    product = Product.query.filter_by(name = name).first()
    reco1 = Product.query.filter_by(image = "1").first()
    reco2 = Product.query.filter_by(image = "2").first()
    reco3 = Product.query.filter_by(image = "3").first()
    reco4 = Product.query.filter_by(image = "4").first()
    reco5 = Product.query.filter_by(image = "5").first()
    form = PurchaseForm() #sur cette page on ajoute un bouton pour acheter un produit
    return render_template('main/product_detail.html', product = product, form = form, reco1 = reco1, reco2 = reco2, reco3 = reco3, reco4 = reco4, reco5 = reco5 )

@bp.route('/cart')
@login_required
def cart():
    form1 = PurchaseForm() #form pour retirer du panier (= même en python que pour ajouter un produits
    form2 = Close() #bouton pour partir et se lougout
    query = current_user.purchases.select()
    cart_products = db.session.scalars(query).all()
    return render_template('main/cart.html', cart_products = cart_products, form1 = form1,form2 = form2 )

@bp.route('/purchase/<name>', methods=['POST'])
@login_required
def purchase(name):
    product = Product.query.filter_by(name=name).first()
    current_user.add_to_cart(product)
    db.session.commit()
    flash('Ton article {} a été rajouté au panier!'.format(name))
    return redirect(url_for('main.recommendation'))

@bp.route('/unpurchase/<name>', methods=['POST'])
@login_required
def unpurchase(name):
    product = Product.query.filter_by(name=name).first()
    current_user.remove_from_cart(product)
    db.session.commit()
    flash('Ton article {} a été retiré de votre panier!'.format(name))
    return redirect(url_for('main.cart'))

