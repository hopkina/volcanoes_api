from flask import jsonify
from geoalchemy2.shape import to_shape
from shapely import geometry


def format_volcano_data(volcano):
    longitude_rounded = round(volcano.longitude, 6)
    latitude_rounded = round(volcano.latitude, 6)
    return {
        'type': 'Feature',
        'properties': {'name': volcano.name, 'id': volcano.id},
        'geometry': {'type': 'Point', 'coordinates': [longitude_rounded, latitude_rounded]},
    }


def format_area_data(country, continent=None, mode=None):
    relevant_area = continent or country

    coordinates = _get_coordinates_for_mode(continent, country, mode)

    return {
        'type': 'Feature',
        'properties': {'name': relevant_area.name, 'id': relevant_area.id},
        'geometry': {'type': 'MultiPolygon', 'coordinates': coordinates},
    }


def _get_coordinates_for_mode(continent, country, mode):
    if mode is None:
        coordinates = [geometry.geo.mapping(to_shape(country.geom))]
    elif mode == 'truncated':
        coordinates = '[Truncated]'
    elif mode == 'smapping':
        coordinates = [geometry.geo.mapping(to_shape(continent.geom))['coordinates']]
    else:
        raise ValueError('Invalid mode given')
    return coordinates


def as_json(data):
    return jsonify({'type': 'FeatureCollection', 'features': data})