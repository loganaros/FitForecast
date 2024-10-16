from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CustomizeForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    vibe = StringField('Vibe', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField('Submit')
