from app.main import bp
from flask import render_template, flash, redirect, url_for, current_app, make_response
from flask_login import current_user, login_required
from app.models import User, Product
from flask import request
from app.main.forms import PurchaseForm
from app.auth.forms import Close
from app import db
from app.models import create_star_table, star_save, star_avg, star_get
import pandas as pd

#Route vers la page d'accueil
@bp.route('/main')
@login_required
def main():
    reco1 = Product.query.filter_by(image = "2").first()
    reco2 = Product.query.filter_by(image = "1").first()
    reco3 = Product.query.filter_by(image = "3").first()
    reco4 = Product.query.filter_by(image = "4").first()
    reco5 = Product.query.filter_by(image = "6").first()
    form = PurchaseForm()
    return render_template('main/main.html', form = form, reco1 = reco1, reco2 = reco2, reco3 = reco3, reco4 = reco4, reco5 = reco5 )

#route vers une page de catégorie 
@bp.route('/sandw')
@login_required
def sandw():
    im = {''}
    page = request.args.get('page',1,type = int) #création des caract de la pagination d'une page 
    sandw = Product.query.filter_by(feature_1 = "Sandw").paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False) # on ajoute la pagination à notre app de base 
    next_url = url_for('main.sandw', page=sandw.next_num) \
        if sandw.has_next else None
    prev_url = url_for('main.sandw', page=sandw.prev_num) \
        if sandw.has_prev else None
    print(sandw.items)
    print(next_url)
    print(prev_url)
    return render_template('main/sandw.html', sandw = sandw.items, next_url=next_url,
                           prev_url=prev_url)

#route vers une page de catégorie 
@bp.route('/salade')
@login_required
def salade():
    page = request.args.get('page',1,type = int) #création des caract de la pagination d'une page 
    sal = Product.query.filter_by(feature_1 = "Salad").paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False) # on ajoute la pagination à notre app de base 
    next_url = url_for('main.salade', page=sal.next_num) \
        if sal.has_next else None
    prev_url = url_for('main.salade', page=sal.prev_num) \
        if sal.has_prev else None
    return render_template('main/salades.html', sal = sal.items, next_url=next_url,
                           prev_url=prev_url)

#route vers la première phase de l'experience
@bp.route('/rate')
@login_required
def rate():
    df = pd.read_csv('app/static/train_entries.csv', delimiter=";")  # to be replaced later on by DB
    products_to_rate = df.loc[df['user_id'] == current_user.id, "product_id"].values

    produit1 = db.session.query(Product).filter_by(id = str(products_to_rate[0])).first()
    produit2 = db.session.query(Product).filter_by(id = str(products_to_rate[1])).first()

    astar = 1
    ustar = 1
    astarbis = 1
    ustarbis = 1
    return render_template("main/rate.html", astar=astar, ustar=ustar,astarbis=astarbis, ustarbis=ustarbis, produit1 = produit1, produit2 = produit2)


# (C) SAVE STARS
@bp.route("/save/", methods=["POST"])
def save():
  uid = current_user.code
  prod1 = Product.query.filter_by(im = current_user.prod4).first()
  pid = int(prod1.id)
  data = dict(request.form)
  star_save(pid, uid, data["stars"])
  return make_response("OK", 200)


@bp.route("/save2/", methods=["POST"])
def save2():
  uid = current_user.code
  prod2 = Product.query.filter_by(im = current_user.prod5).first()
  pid2 = int(prod2.id)
  data = dict(request.form)
  star_save(pid2, uid, data["stars2"])
  return make_response("OK", 200)


#Route vers une page produit
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
    return render_template('main/product_page.html', product = product, form = form, reco1 = reco1, reco2 = reco2, reco3 = reco3, reco4 = reco4, reco5 = reco5 )

#Route vers une page panier
@bp.route('/cart')
@login_required
def cart():
    form1 = PurchaseForm() #form pour retirer du panier (= même en python que pour ajouter un produits
    form2 = Close() #bouton pour partir et se lougout
    query = current_user.bought_products.select()
    cart_products = db.session.scalars(query).all()
    #cart_products = current_user.bought_products.all()
    return render_template('main/cart.html', cart_products = cart_products, form1 = form1,form2 = form2 )

@bp.route('/purchase/<name>', methods=['POST'])
@login_required
def purchase(name):
    product = Product.query.filter_by(name=name).first()
    current_user.add(product)
    db.session.commit()
    flash('Ton article {} a été rajouté au panier!'.format(name))
    return redirect(url_for('main.main'))

@bp.route('/unpurchase/<name>', methods=['POST'])
@login_required
def unpurchase(name):
    product = Product.query.filter_by(name=name).first()
    current_user.remove(product)
    db.session.commit()
    flash('Ton article {} a été retiré de votre panier!'.format(name))
    return redirect(url_for('main.cart'))

