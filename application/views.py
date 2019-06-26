from flask import render_template, jsonify, redirect, request
from geoalchemy2.shape import to_shape
from shapely import geometry

from application.decorators import as_feature_collection
from application.formatters import format_volcano_data, format_area_data, as_json
from .forms import *
from .models import *


# A redirecting URL that pushes to the volcanoes URL
ENDPOINTS = [
    {'name': 'Volcano', 'endpoint': '/volcano'},
    {'name': 'Country', 'endpoint': '/country'},
    {'name': 'Continent', 'endpoint': '/continent'},
]


@app.route('/', methods=['GET'])
def get_api():
    # return redirect(url_for('volcano'))
    return redirect('/volcano/api/v0.1')


@app.route('/volcano/api/v0.1', methods=['GET'])
def get_endpoints():
    return jsonify({'endpoints': ENDPOINTS})


@app.route('/volcano/api/v0.1/volcano', methods=['GET'])
@as_feature_collection
def get_volcanoes():
    volcanoes_queryset = session.query(Volcano).all()
    data = [format_volcano_data(volcano) for volcano in volcanoes_queryset]

    return data


@app.route('/volcano/api/v0.1/volcano/<int:volcano_id>', methods=['GET'])
@as_feature_collection
def get_volcano(volcano_id):
    volcano = session.query(Volcano).get(volcano_id)
    data = [format_volcano_data(volcano)]

    return data


@app.route('/volcano/api/v0.1/volcano/<volcano_name>', methods=['GET'])
@as_feature_collection
def get_volcano_name(volcano_name):
    volcanoes_queryset = session.query(Volcano).filter(Volcano.name.like(volcano_name + "%")).all()
    data = [format_volcano_data(volcano) for volcano in volcanoes_queryset]

    return data


@app.route('/volcano/api/v0.1/volcano/<int:volcano_id>/intersect', methods=['GET'])
def volcano_intersect(volcano_id):
    volcano = session.query(Volcano).get(volcano_id)
    country = session.query(Country).filter(Country.geom.ST_Intersects(volcano.geom)).first()

    if country is None:
        return redirect('/volcano/api/v0.1/volcano/' + str(volcano_id))

    continent = session.query(Continent).filter(Continent.geom.ST_Intersects(volcano.geom)).first()

    data = [
        format_volcano_data(volcano),
        format_area_data(country),
        format_area_data(country, continent=continent),
    ]

    return as_json(data)


@app.route('/volcano/api/v0.1/country', methods=['GET'])
@as_feature_collection
def get_countries():
    countries = session.query(Country).all()
    geoms = {country.id: geometry.geo.mapping(to_shape(country.geom)) for country in countries}

    data = [
        {"type": "Feature",
         "properties": {"name": country.name, "continent": country.continent.name},
         "geometry": {"type": "MultiPolygon", "coordinates": geoms[country.id]["coordinates"]},
         }
        for country in countries
    ]

    return data


@app.route('/volcano/api/v0.1/country/<int:country_id>/within', methods=['GET'])
@as_feature_collection
def get_country_volcanoes(country_id):
    country = session.query(Country).get(country_id)

    volcanoes_queryset = session.query(Volcano).filter(Volcano.geom.ST_Within(country.geom))
    data = [format_volcano_data(volcano) for volcano in volcanoes_queryset]

    return data


@app.route('/volcano/api/v0.1/continent', methods=['GET'])
@as_feature_collection
def get_continents():
    continents = session.query(Continent).all()

    mode = 'truncated'
    if 'geometry' in request.args.keys():
        if request.args['geometry'] == '1' or request.args['geometry'] == 'True':
            mode = 'smapping'

    data = [format_area_data(None, continent=continent, mode=mode) for continent in continents]

    return data


# this function accepts web requests, finding data about each volcano 
# contained within the volcanoes data table
@app.route('/volcanoes', methods=["GET", "POST"])
def volcanoes():
    volcanoes = session.query(Volcano).all()

    form = VolcanoForm(request.form)
    form.selections.choices = [(volcano.id, volcano.name) for volcano in volcanoes]
    form.popup = "Select a volcano"
    form.latitude = 15.130007
    form.longitude = 120.350001

    if request.method == "POST":

        volcano_id = form.selections.data
        volcano = session.query(Volcano).get(volcano_id)
        form.longitude = round(volcano.longitude, 4)
        form.latitude = round(volcano.latitude, 4)

        country = session.query(Country).filter(Country.geom.ST_Contains(volcano.geom)).first()
        if country is not None:
            continent = session.query(Continent).filter(Continent.geom.ST_Intersects(volcano.geom)).first()
            form.popup = f"The {volcano.name} volcano is located at {form.longitude}, {form.latitude}, " \
                f"which is in {country.name}, {continent.name}."
        else:
            form.popup = "The country, and continent could not be located using point in polygon analysis"

        return render_template('index.html', form=form)
    return render_template('index.html', form=form)
