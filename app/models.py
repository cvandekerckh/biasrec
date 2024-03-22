import os

from app import db
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import login
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Purchase Table
purchases = db.Table(
    'purchases',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
)

# User table
class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    code: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    bought_products: so.WriteOnlyMapped['Product'] = so.relationship(
        secondary=purchases,
        back_populates='buyers',
    )

    def __repr__(self): #Pour print les objets de cette classe 
        return '<User {}>'.format(self.code)
    
    def add(self, product):
        if not self.has_bought(product):
            self.bought_products.add(product)

    def remove(self, product):
        if self.has_bought(product):
            self.bought_products.remove(product)

    def has_bought(self, product):
        query = self.bought_products.select().where(Product.id == product.id)
        return db.session.scalar(query) is not None


# Product table
class Product(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    feature_1: so.Mapped[str] = so.mapped_column(sa.String(64))
    feature_2: so.Mapped[str] = so.mapped_column(sa.String(64))
    feature_3: so.Mapped[str] = so.mapped_column(sa.String(64))
    feature_4: so.Mapped[str] = so.mapped_column(sa.String(64))
    price: so.Mapped[str] = so.mapped_column(sa.String(64))
    image: so.Mapped[str] = so.mapped_column(sa.String(64))
    nutri_score: so.Mapped[str] = so.mapped_column(sa.String(64))

    buyers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=purchases,
        back_populates='bought_products',
    )

    def __repr__(self):
        return '<Product {}>'.format(self.name)
    

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
