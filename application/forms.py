from flask_wtf import FlaskForm
from wtforms import SelectField


class VolcanoForm(FlaskForm):
	description  = "Use the dropdown to select a volcano."
	selections = SelectField('Select a volcano',choices=[])
