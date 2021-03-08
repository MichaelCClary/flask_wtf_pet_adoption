from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, TextAreaField, SelectField
from wtforms.validators import InputRequired, URL, Optional, NumberRange
from wtforms.widgets.html5 import NumberInput

species = ['Cat', 'Dog', 'Porcupine']


class PetForm(FlaskForm):
    name = StringField("Pet Name", validators=[
                       InputRequired(message="Pet Name Required")])
    species = SelectField("Pet Species", choices=[(sp, sp) for sp in species])
    photo_url = StringField("URL for Pet Picture", validators=[
                            Optional(), URL(message="Must be a valid URL")])
    age = IntegerField("Age", widget=NumberInput(
        min=0, max=30, step=1), validators=[Optional()])
    notes = TextAreaField("Notes")
    available = BooleanField("Available")
