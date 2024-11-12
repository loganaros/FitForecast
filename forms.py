from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class CustomizeForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    vibe = StringField('Vibe', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SaveOutfitForm(FlaskForm):
    name = StringField('Name Your Outfit', validators=[DataRequired()])
    submit = SubmitField('Save Outfit')