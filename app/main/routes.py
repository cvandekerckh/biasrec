from app.main import bp
from flask import render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from app.models import User, Product
from flask import request
from app.main.forms import PurchaseForm
from app.auth.forms import Close
from app import db

#Route vers la page d'accueil
@bp.route('/main')
@login_required
def main():
    reco1 = Product.query.filter_by(im = "2").first()
    reco2 = Product.query.filter_by(im = "1").first()
    reco3 = Product.query.filter_by(im = "3").first()
    reco4 = Product.query.filter_by(im = "4").first()
    reco5 = Product.query.filter_by(im = "6").first()
    form = PurchaseForm()
    return render_template('main/main.html', form = form, reco1 = reco1, reco2 = reco2, reco3 = reco3, reco4 = reco4, reco5 = reco5 )

#route vers une page de catégorie 
@bp.route('/sandw')
@login_required
def sandw():
    im = {''}
    page = request.args.get('page',1,type = int) #création des caract de la pagination d'une page 
    sandw = Product.query.filter_by(c0 = "Sandw").paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False) # on ajoute la pagination à notre app de base 
    next_url = url_for('main.sandw', page=sandw.next_num) \
        if sandw.has_next else None
    prev_url = url_for('main.sandw', page=sandw.prev_num) \
        if sandw.has_prev else None
    return render_template('main/sandw.html', sandw = sandw.items, next_url=next_url,
                           prev_url=prev_url)

#route vers une page de catégorie 
@bp.route('/salade')
@login_required
def salade():
    page = request.args.get('page',1,type = int) #création des caract de la pagination d'une page 
    sal = Product.query.filter_by(c0 = "Salad").paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False) # on ajoute la pagination à notre app de base 
    next_url = url_for('main.salade', page=sal.next_num) \
        if sal.has_next else None
    prev_url = url_for('main.salade', page=sal.prev_num) \
        if sal.has_prev else None
    return render_template('main/salades.html', sal = sal.items, next_url=next_url,
                           prev_url=prev_url)

#Route vers une page produit
@bp.route('/product/<title>')
@login_required
def product(title):
    product = Product.query.filter_by(title = title).first()
    reco1 = Product.query.filter_by(im = "1").first()
    reco2 = Product.query.filter_by(im = "2").first()
    reco3 = Product.query.filter_by(im = "3").first()
    reco4 = Product.query.filter_by(im = "4").first()
    reco5 = Product.query.filter_by(im = "5").first()
    form = PurchaseForm() #sur cette page on ajoute un bouton pour acheter un produit
    return render_template('main/product_page.html', product = product, form = form, reco1 = reco1, reco2 = reco2, reco3 = reco3, reco4 = reco4, reco5 = reco5 )

#Route vers une page panier
@bp.route('/cart')
@login_required
def cart():
    form1 = PurchaseForm() #form pour retirer du panier (= même en python que pour ajouter un produits
    form2 = Close() #bouton pour partir et se lougout
    cart_products = current_user.products_bought.all()
    return render_template('main/cart.html', cart_products = cart_products, form1 = form1,form2 = form2 )

@bp.route('/purchase/<title>', methods=['POST'])
@login_required
def purchase(title):
    product = Product.query.filter_by(title=title).first()
    current_user.add(product)
    db.session.commit()
    flash('Ton article {} a été rajouté au panier!'.format(title))
    return redirect(url_for('main.main'))

@bp.route('/unpurchase/<title>', methods=['POST'])
@login_required
def unpurchase(title):
    product = Product.query.filter_by(title=title).first()
    current_user.remove(product)
    db.session.commit()
    flash('Ton article {} a été retiré de votre panier!'.format(title))
    return redirect(url_for('main.cart'))

