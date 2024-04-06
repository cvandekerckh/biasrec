from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Creation du bouton pour quitter l'enquête et se lougout 
class Close(FlaskForm):
    submit = SubmitField('Finish and go to survey')

class LogoutForm(FlaskForm):
    submit = SubmitField('Logout') 
