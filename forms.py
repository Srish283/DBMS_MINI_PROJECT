from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
  firstname = StringField('First Name', validators=[DataRequired()])
  lastname=StringField('Last Name', validators=[DataRequired()])
  number=IntegerField('Number', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('SignUp')    

class LoginForm(FlaskForm):
  #username=StringField('Username', validators=[DataRequired()])
  email = StringField('Email',validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember = BooleanField('Remember Me')
  submit = SubmitField('Login')  