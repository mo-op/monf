from flask import Flask, render_template, request
from flask import jsonify
from flask_pymongo import PyMongo
from forms import QueryForm, VizForm, MapForm
import folium
import pandas as pd
from decimal import Decimal
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter

import sys
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app._static_folder = "static"

app.config['MONGO_DBNAME'] = 'cities'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/cities'
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"))

mongo = PyMongo(app)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/queries',methods=['GET','POST'])
def queries():
	form = QueryForm()
	cities = mongo.db.cities
	citiesData = []
	holder = cities.find().sort("population",1)
	for city in holder:
	 	citiesData.append({'name': city['name'] , 'population': city['population']})
	#citiesData = jsonify(citiesData)
	#print citiesData[]
	query={}
	if request.method == 'POST':
		result = []
		if (request.form['sort']=='D'):
			key = -1
		else:
			key= 1
		#country only and country and continent 
		if (request.form['country']):
			cty = request.form['country']
			for city in cities.find({'country':cty}).sort('population',key):
				result.append({'name': city['name'] , 'population': city['population']})
		#none
		elif (not request.form['country'] and request.form['continent']=='Unspecified'):
			holder = cities.find().sort('population',key)
			for city in holder:
	 			result.append({'name': city['name'] , 'population': city['population']})
	 	#continent only
		elif (not request.form['country'] and request.form['continent']!='Unspecified'):	
			holder = cities.find({"timeZone" : {'$regex' : '.*' + request.form['continent'] + '.*'}}).sort('population',key)
			for city in holder:
				result.append({'name': city['name'] , 'population': city['population']})

		else:
			result = str("Try again!")
		return render_template('queries.html',form=form,citiesData=result)

	return render_template('queries.html', form=form, citiesData=citiesData)

@app.route('/visualize', methods=['GET','POST'])
def visualize():
	form = VizForm()
	data_city_high = []
	data_city_low = []
	data_country_high = []
	data_country_low = []
	data_city = []

	cities = mongo.db.cities
	lati = 'x'
	longi = 'y'

	for city in cities.find().sort("population",-1).limit(10):
		lati,longi = str(city['location']['coordinates']).split(',')
		lati = lati.replace("[", "")
		longi = longi.replace("]", "")
		lati = float(lati)
		longi = float(longi)
		data_city_high.append({'name':city['name'],'lat':lati, 'lon':longi, 'pop':city['population']})

	for city in cities.find().sort("population",1).limit(10):
		lati,longi = str(city['location']['coordinates']).split(',')
		lati = lati.replace("[", "")
		longi = longi.replace("]", "")
		lati = float(lati)
		longi = float(longi)
		data_city_low.append({'name':city['name'],'lat':lati, 'lon':longi, 'pop':city['population']})
	
	data_country= []
	pipeline = [{'$group': {'_id': '$country','sum_pop': {'$sum': '$population'} } } ]
			#data = cities.command('aggregate', 'cities', pipeline=pipeline)
	data = (cities.aggregate(pipeline)['result'])
	for city in data:
		data_country.append({'country':city['_id'].encode('utf-8'), 'population':city['sum_pop']})


	if request.method == 'POST':
		#case 1
		if (request.form['choice']=='top10ch'):
			lat = []
			lon = []
			name = []
			for city in data_city_high:
				lat.append(city['lat'])
				lon.append(city['lon'])
				name.append(str(city['name']+","+str(city['pop'])))
			data = pd.DataFrame({'lat':lat, 'lon':lon, 'name':name})
			m = folium.Map(location=[20, 0], tiles="Mapbox Bright", zoom_start=2)
			for i in range(0,len(data)):
				folium.Marker([data.iloc[i]['lon'], data.iloc[i]['lat']], popup=data.iloc[i]['name']).add_to(m)
			m.save('templates/map1.html')
			return render_template('visualize.html', form=form, map='map1.html')
		#case 2
		elif (request.form['choice']=='low10cl'):
			lat = []
			lon = []
			name = []
			for city in data_city_low:
				lat.append(city['lat'])
				lon.append(city['lon'])
				name.append(str(city['name']+","+str(city['pop'])))
			data = pd.DataFrame({'lat':lat, 'lon':lon, 'name':name})
			m = folium.Map(location=[20, 0], tiles="Mapbox Bright", zoom_start=2)
			for i in range(0,len(data)):
				folium.Marker([data.iloc[i]['lon'], data.iloc[i]['lat']], popup=data.iloc[i]['name']).add_to(m)
			m.save('templates/map2.html')
			return render_template('visualize.html', form=form, map='map2.html')
		#case 3 
		elif (request.form['choice']=='top10th'):	
			data_country_h = sorted(data_country, key=lambda k: k['population'],reverse=True) 
				#data_country_high.append({'country':name,'population':pop})
			# return render_template('visualize.html', form=form,map='map3.html')
			for i in range(10):
				data_country_high.append(data_country_h[i])

			pop = []
			names = []
			for i in data_country_high:
				pop.append(i['population'])
				names.append(i['country'])
			df = pd.DataFrame({'country':names, 'population':pop})
			my_range=range(1,len(df.index)+1)
			
 
# The vertival plot is made using the hline function
# I load the seaborn library only to benefit the nice looking feature
			import seaborn as sns
			plt.hlines(y=my_range, xmin=0, xmax=df['population'], color='skyblue')
			plt.plot(df['population'], my_range, "o")
			 
			# Add titles and axis names
			plt.yticks(my_range,df['country'])
			plt.title("Population : Countries", loc='left')
			plt.xlabel('population')
			plt.ylabel('Country')
			#plt.save_html('templates/map3.html')
			plt.savefig('static/plot1.png',bbox_inches='tight')
			return render_template('visualize.html', form=form,img="static/plot1.png")

		#case 4
		elif (request.form['choice']=='low10tl'):
			data_country_l = sorted(data_country, key=lambda k: k['population']) 
				#data_country_high.append({'country':name,'population':pop})
			# return render_template('visualize.html', form=form,map='map3.html')
			for i in range(10):
				data_country_low.append(data_country_l[i])

			pop = []
			names = []
			for i in data_country_low:
				pop.append(i['population'])
				names.append(i['country'])
			df = pd.DataFrame({'country':names, 'population':pop})
			my_range=range(1,len(df.index)+1)
			
 
# The vertival plot is made using the hline function
# I load the seaborn library only to benefit the nice looking feature
			import seaborn as sns
			plt.hlines(y=my_range, xmin=0, xmax=df['population'], color='skyblue')
			plt.plot(df['population'], my_range, "o")
			 
			# Add titles and axis names
			plt.yticks(my_range,df['country'])
			plt.title("Population : Countries", loc='left')
			plt.xlabel('population')
			plt.ylabel('Country')
			#plt.save_html('templates/map3.html')
			plt.savefig('static/plot2.png',bbox_inches='tight')
			return render_template('visualize.html', form=form,img="static/plot2.png")

		else:
			return render_template('visualize.html', form=form)


	return render_template('visualize.html', form=form)

@app.route('/coordinates', methods=['GET','POST'])
def coordinates():
	form = MapForm()
	cities = mongo.db.cities
	data_city = []
	lat = []
	lon = []
	name = []
	pop = []

	if (request.method == 'POST'):
		if ((request.form['latitude']) and (request.form['longitude'])):
			
			for city in cities.find().sort("population",-1):
				lati,longi = str(city['location']['coordinates']).split(',')
				lati = lati.replace("[", "")
				longi = longi.replace("]", "")
				lati = float(lati)
				longi = float(longi)
				data_city.append({'name':city['name'],'lat':lati, 'lon':longi, 'pop':city['population']})

			for city in data_city:
				if ((city['lat'] == float(request.form['latitude'])) and (city['lon']==float(request.form['longitude']))):
					lat.append(city['lat'])
					lon.append(city['lon'])
					name.append(str(city['name']+","+str(city['pop'])))
					pop.append(city['pop'])
					break

			data = pd.DataFrame({'lat':lat, 'lon':lon, 'name':name,'pop':pop})
			m = folium.Map(location=[20, 0], tiles="Mapbox Bright", zoom_start=2)
			for i in range(0,len(data)):
				folium.Circle([data.iloc[i]['lon'], data.iloc[i]['lat']], popup=data.iloc[i]['name'],radius=data.iloc[i]['pop']*10,color='crimson',fill=True,fill_color='crimson').add_to(m)
			m.save('templates/map5.html')
			return render_template('visualize2.html',form=form,map='map5.html')

		else:
			error = "Enter valid points!"
			return render_template('visualize2.html',form=form,error=error)
	return render_template('visualize2.html', form=form)

if __name__ == '__main__':
   app.run(debug = True)