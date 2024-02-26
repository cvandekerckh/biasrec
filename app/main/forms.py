from flask_wtf import FlaskForm
from wtforms import SubmitField

class PurchaseForm(FlaskForm):
    submit = SubmitField('Add to cart')
