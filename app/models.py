from app import db
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

purchase = db.Table('purchase',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
                    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), index=True, unique=True)
    products_bought = db.relationship('Product', secondary=purchase, backref='users_who_bought', lazy='dynamic')

    def __repr__(self): #Pour print les objets de cette classe 
        return '<User {}>'.format(self.code)
    
    # 3 fonctions pour ajouter ou retirer un produit au panier
    def add(self, product):
        if not self.has_bought(product):
            self.products_bought.append(product)

    def remove(self, product):
        if self.has_bought(product):
            self.products_bought.remove(product)

    def has_bought(self, product):
        return self.products_bought.filter(
            purchase.c.product_id == product.id).count() > 0 #On filtre le produit qui nous intéresse parmi tous les produits achetés par le user
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    c0=db.Column(db.String(100))
    c1=db.Column(db.String(100))
    c2=db.Column(db.String(100))
    c3=db.Column(db.String(100))
    price=db.Column(db.String(100))
    im= db.Column(db.String(100))
    nutri = db.Column(db.String(100))

    def __repr__(self):
        return '<Product {}>'.format(self.title)
    


    

