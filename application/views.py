from application import app

from flask import render_template, jsonify, redirect, url_for, request, Markup
import geoalchemy2, shapely
from shapely import geometry
from geoalchemy2.shape import to_shape

from .forms import *	
from .models import *

# A redirecting URL that pushes to the volcanoes URL
@app.route('/', methods=['GET'])
def get_api():
	# return redirect(url_for('volcano'))
	return redirect('/volcano/api/v0.1')


@app.route('/volcano/api/v0.1', methods=['GET'])
def get_endpoints():
	data = [{'name': 'Volcano', 'endpoint':  '/volcano'},
			{'name': 'Country', 'endpoint': '/country'},
			{'name': 'Continent', 'endpoint': '/continent'},]
	return jsonify({'endpoints':data})


@app.route('/volcano/api/v0.1/volcano', methods=['GET'])
def get_volcanoes():
	volcanoes = session.query(Volcano).all()
	data = [{'type': 'Feature', 
			 'properties': {'name': volcano.name, 'id': volcano.id},
			 'geometry': {'type': 'Point', 
			 			  'coordinates': [round(volcano.longitude, 6), 
						   				  round(volcano.latitude, 6)]},
			} for volcano in volcanoes]
	
	return jsonify({'type': 'FeatureCollection', 'features': data})


@app.route('/volcano/api/v0.1/volcano/<int:volcano_id>', methods=['GET'])
def get_volcano(volcano_id):
	volcano = session.query(Volcano).get(volcano_id)
	data = [{'type': 'Feature', 
			 'properties': {'name': volcano.name, 'id': volcano.id},
			 'geometry': {'type': 'Point', 
			 			  'coordinates': [round(volcano.longitude, 6), 
						   				  round(volcano.latitude, 6)]},}]

	return jsonify({'type': 'FeatureCollection', 'features': data})


@app.route('/volcano/api/v0.1/volcano/<volcano_name>', methods=['GET'])
def get_volcano_name(volcano_name):
	volcanoes = session.query(Volcano).filter(Volcano.name.like(volcano_name+"%")).all()
	data = [{'type': 'Feature', 
			 'properties': {'name': volcano.name, 'id': volcano.id},
			 'geometry': {'type': 'Point', 
			 			  'coordinates': [round(volcano.longitude, 6), 
						   				  round(volcano.latitude, 6)]},
			} for volcano in volcanoes]

	return jsonify({'type': 'FeatureCollection', 'features': data})


@app.route('/volcano/api/v0.1/volcano/<int:volcano_id>/intersect', methods=['GET'])
def volcano_intersect(volcano_id):
	volcano = session.query(Volcano).get(volcano_id)
	country = session.query(Country).filter(Country.geom.ST_Intersects(volcano.geom)).first()
	continent = session.query(Continent).filter(Continent.geom.ST_Intersects(volcano.geom)).first()

	if country != None:

		data = [{'type': 'Feature', 
			 	 'properties': {'name': volcano.name, 'id': volcano.id},
			 	 'geometry': {'type': 'Point', 
			 			  	  'coordinates': [round(volcano.longitude, 6), 
						   				  	  round(volcano.latitude, 6)]},
				},
				{'type': 'Feature',
				 'properties': {'name': country.name, 'id': country.id},
				 'geometry': {'type': 'MultiPolygon', 
			 			  	  'coordinates': [shapely.geometry.geo.mapping(to_shape(country.geom))]},
				},
				{'type': 'Feature',
				 'properties': {'name': continent.name, 'id': continent.id},
				 'geometry': {'type': 'MultiPolygon',
				 			  'coordinates': [shapely.geometry.geo.mapping(to_shape(country.geom))]}
				}]

		return jsonify({'type': 'FeatureCollection', 'features': data})
	
	else:
		return redirect('/volcano/api/v0.1/volcano/' + str(volcano_id))


@app.route('/volcano/api/v0.1/country', methods=['GET'])
def get_countries():
	countries = session.query(Country).all()
	geoms = {country.id:shapely.geometry.geo.mapping(to_shape(country.geom)) for country in countries}

	data = [{"type": "Feature",	
			 "properties":{"name":country.name, "continent":country.continent.name}, 
			 "geometry":{"type":"MultiPolygon",	
			 "coordinates":geoms[country.id]["coordinates"]},
			} for country in countries]

	return jsonify({"type": "FeatureCollection","features":data})


@app.route('/volcano/api/v0.1/country/<int:country_id>/within', methods=['GET'])
def get_country_volcanoes(country_id):
	
	country = session.query(Country).get(country_id)
	# shp = to_shape(country.geom)
	# geojson = shapely.geometry.geo.mapping(shp)

	# data = [{"type": "Feature",
	# 		 "properties":{"name":country.name,"id":country.id}, 
	# 		 "geometry":{"type":"MultiPolygon",	
	# 		 "coordinates":[geojson]},
	# }]

	volcanoes = session.query(Volcano).filter(Volcano.geom.ST_Within(country.geom))
	data_volcanoes =[{"type": "Feature",
				   	  "properties":{"name":volcano.name}, 
					  "geometry":{"type":"Point",	
					  "coordinates":[round(volcano.longitude,6), round(volcano.latitude,6)]}, 
					 } for volcano in volcanoes]

	# data.extend(data_volcanoes)

	return jsonify({"type": "FeatureCollection","features":data_volcanoes})


@app.route('/volcano/api/v0.1/continent', methods=['GET'])
def get_continents():
	smapping = shapely.geometry.geo.mapping
	continents = session.query(Continent).all()

	data = [{'type': 'Feature', 
			 'properties': {'continent': continent.name, 'id': continent.id},
			 'geometry': {'type': 'MultiPolygon', 
			 			  'coordinates': '[Truncated]'},
			} for continent in continents]
	
	if 'geometry' in request.args.keys():
		if request.args['geometry'] == '1' or request.args['geometry'] == 'True':
			data = [{'type': 'Feature', 
					 'properties': {'continent': continent.name, 'id': continent.id},
					 'geometry': {'type': 'MultiPolygon', 
								  'coordinates': [smapping(to_shape(continent.geom))['coordinates']]},
					} for continent in continents]

	return jsonify({'type': 'FeatureCollection', 'features': data})


# this function accepts web requests, finding data about each volcano 
# contained within the volcanoes data table
@app.route('/volcanoes', methods=["GET","POST"])
def volcanoes():
	form = VolcanoForm(request.form)

	volcanoes = session.query(Volcano).all()
	form.selections.choices = [(volcano.id, volcano.name) for volcano in volcanoes]
	form.popup = "Select a volcano"
	form.latitude = 15.130007
	form.longitude = 120.350001

	if request.method == "POST":

		volcano_id = form.selections.data
		volcano = session.query(Volcano).get(volcano_id)
		form.longitude = round(volcano.longitude,4)
		form.latitude = round(volcano.latitude,4)

		country = session.query(Country).filter(Country.geom.ST_Contains(volcano.geom)).first()
		if country != None:
			continent = session.query(Continent).filter(Continent.geom.ST_Intersects(volcano.geom)).first()
			form.popup = ("The {0} volvano is located at {3}, {4}, which is in {1}, {2}."
				.format(volcano.name, 
						country.name, 
						continent.name, 
						form.longitude, 
						form.latitude))
		else:
			form.popup = "The country, and continent could not be located using point in polygon analysis"

		return render_template('index.html',form=form)
	return render_template('index.html',form=form)
