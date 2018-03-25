from flask import Flask
from flask.ext.pymongo import PyMongo 

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'cities'
app.config['MONGO_URI'] = 'mongodb://dbuser:db00@ds117469.mlab.com:17469/cities'

mongo = PyMongo(app) 	