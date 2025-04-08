from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    code = StringField('Login', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Creation du bouton pour quitter l'enquête et se lougout 
class Close(FlaskForm):
    submit = SubmitField('Finish and go to survey') 
