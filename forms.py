from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField

from wtforms import validators, ValidationError

class QueryForm(Form):
   country = TextField("Country")
   sort = RadioField('Sort By', choices = [('A','Ascending'),('D','Descending')])
   continent = SelectField('Continent', choices = [('Unspecified','Unspecified'),('Africa', 'Africa'), ('Asia', 'Asia'),('Australia','Australia'),('Europe', 'Europe'),('America','America')])
   submit = SubmitField("Send")

class VizForm(Form):
	choice = SelectField('Visuals', choices=[('top10ch','Top 10 Cities: Highest'),('low10cl','Bottom 10 Cities: Lowest'),('top10th','Top 10 Countries: Highest'),('low10tl','Bottom 10 Countries: Lowest')])
	submit = SubmitField("Submit")

class MapForm(Form):
	latitude = TextField("Latitude")
	longitude = TextField("Longitude")
	submit = SubmitField("Send")
