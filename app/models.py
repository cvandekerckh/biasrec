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

# Assigned for training
training = db.Table(
    'training',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
)

# Assigned

# User table
class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    code: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    condition_id: so.Mapped[int] = so.mapped_column(sa.Integer)
    purchases: so.WriteOnlyMapped['Product'] = so.relationship(
        secondary=purchases,
        back_populates='buyers',
    )

    ratings: so.WriteOnlyMapped['Rating'] = so.relationship(
        'Rating',
        back_populates='user',
    )

    assignments: so.WriteOnlyMapped['Product'] = so.relationship(
        secondary=training,
        back_populates='assigned_users',
    )

    def __repr__(self): #Pour print les objets de cette classe 
        return '<User {}>'.format(self.code)

    def has_bought(self, product):
        query = self.purchases.select().where(Product.id == product.id)
        return db.session.scalar(query) is not None

    def add_to_cart(self, product):
        if not self.has_bought(product):
            self.purchases.add(product)

    def remove_from_cart(self, product):
        if self.has_bought(product):
            self.purchases.remove(product)

    def is_assigned(self, product):
        query = self.assignments.select().where(Product.id == product.id)
        return db.session.scalar(query) is not None

    def assign_product(self, product):
        if not self.is_assigned(product):
            self.assignments.add(product)

    def add_rating(self, product_id, rating):
        session = db.session()
        existing_rating = session.query(Rating).filter_by(user_id=self.id, product_id=product_id).first()
        
        if existing_rating:
            existing_rating.rating = rating
        else:
            new_rating = Rating(user_id=self.id, product_id=product_id, rating=rating)
            session.add(new_rating)
        
        session.commit()

    def get_rating_for_product(self, product_id):
        session = db.session
        query = self.ratings.select().where(Rating.product_id == product_id)
        rating_item = session.scalars(query).first()
        if rating_item is not None:
            return rating_item.rating
        else:
            return None


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
        back_populates='purchases',
    )
    ratings: so.WriteOnlyMapped['Rating'] = so.relationship('Rating', back_populates='product')

    assigned_users: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=training,
        back_populates='assignments',
    )

    def __repr__(self):
        return '<Product {}>'.format(self.name)


# Ratings table
class Rating(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'))
    product_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('product.id'))
    rating: so.Mapped[int] = so.mapped_column(sa.Integer)

    user: so.Mapped['User'] = so.relationship('User', back_populates='ratings')
    product: so.Mapped['Product'] = so.relationship('Product', back_populates='ratings')

    def __repr__(self):
        return '<Rating id={}, user_id={}, product_id={}, rating={}>'.format(self.id, self.user_id, self.product_id, self.rating)