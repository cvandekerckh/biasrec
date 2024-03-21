import os

from app import db
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Purchase Table
purchase = db.Table('purchase',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
                    )

# User table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), index=True, unique=True)
    prod1 = db.Column(db.String(4))
    prod2 = db.Column(db.String(4))
    prod3 = db.Column(db.String(4))
    prod4 = db.Column(db.String(4))
    prod5 = db.Column(db.String(4))
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

# Product table
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
    

# Stars
# (A) LOAD SQLITE MODULE
import sqlite3
DBFILE = "stars.db"

# (B) HELPER - EXECUTE SQL QUERY
def query(sql, data):
  conn = sqlite3.connect(DBFILE)
  cursor = conn.cursor()
  cursor.execute(sql, data)
  conn.commit()
  conn.close()


# (C) HELPER - FETCH
def star_fetch(sql, data=[]):
  conn = sqlite3.connect(DBFILE)
  cursor = conn.cursor()
  cursor.execute(sql, data)
  results = cursor.fetchone()
  conn.close()
  return results

# (D) CREATE/SAVE/UPDATE USER STAR RATING
def create_star_table():
    if os.path.exists(DBFILE):
        os.remove(DBFILE)
    query(
        """CREATE TABLE `star_rating` (
        `product_id` INTEGER  NOT NULL,
        `user_id` INTEGER  NOT NULL,
        `rating` INTEGER NOT NULL DEFAULT '1',
        PRIMARY KEY (`product_id`,`user_id`)
        );""",
        []
    )
    query(
       """INSERT INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES
        (1, 900, 1),
        (1, 901, 2),
        (1, 902, 3),
        (1, 903, 4),
        (1, 904, 5);
        """,
        []
    )
    return True

def star_save(pid, uid, stars):
  rat = star_get(pid, uid)
  if rat is None :
    query(
      "INSERT INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
      [pid, uid, stars]
    )
  else : 
    query(
    "REPLACE INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
    [pid, uid, stars]
    )
  return True

def star_insert(pid, uid, stars):
  rat = star_get(pid, uid)
  if rat is None :
    query(
      "INSERT INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
      [pid, uid, stars]
    )
  else : 
    query(
    "REPLACE INTO `star_rating` (`product_id`, `user_id`, `rating`) VALUES (?,?,?)",
    [pid, uid, stars]
    )
  return True


# (E) GET USER STAR RATING FOR PRODUCT
def star_get(pid, uid):
  res = star_fetch(
    "SELECT * FROM `star_rating` WHERE `product_id`=? AND `user_id`=?",
    [pid, uid]
  )
  return 0 if res is None else res[2]

# (F) GET AVERAGE RATING FOR PRODUCT
def star_avg(pid):
  res = star_fetch("""
    SELECT ROUND(AVG(`rating`), 2) `avg`, COUNT(`user_id`) `num`
    FROM `star_rating`
    WHERE `product_id`=?""", [pid])
  return (0, 0) if res[0] is None else res
