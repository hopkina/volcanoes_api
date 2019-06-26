from unittest import TestCase
from unittest.mock import patch, sentinel, call

from application.formatters import as_json, format_volcano_data, format_area_data


class TestFormatVolcanoData(TestCase):
    class StubVolcano:
        latitude = sentinel.latitude
        longitude = sentinel.longitude
        name = sentinel.name
        id = sentinel.id

    def setUp(self) -> None:
        super().setUp()

        patched_round = patch('builtins.round')
        self._patched_round = patched_round.start()
        self.addCleanup(patched_round.stop)

    def test_rounding(self):
        """Should round volcano locations to 6 DP"""

        expected_args = [call(sentinel.longitude, 6), call(sentinel.latitude, 6)]

        format_volcano_data(self.StubVolcano())

        self.assertEqual(expected_args, self._patched_round.call_args_list)

    def test_result(self):
        """Should return expected results"""

        self._patched_round.side_effect = [sentinel.longitude_rounded, sentinel.latitude_rounded]
        expected_result = {
            'type': 'Feature',
            'properties': {'name': sentinel.name, 'id': sentinel.id},
            'geometry': {
                'type': 'Point',
                'coordinates': [sentinel.longitude_rounded, sentinel.latitude_rounded],
            },
        }

        result = format_volcano_data(self.StubVolcano())

        self.assertEqual(expected_result, result)


class TestFormatAreaData(TestCase):
    class StubCountry:
        id = sentinel.country_id
        name = sentinel.country_name

    class StubContinent:
        id = sentinel.continent_id
        name = sentinel.continent_name

    def setUp(self) -> None:
        super().setUp()

        patched_get_coordinates_for_mode = patch('application.formatters._get_coordinates_for_mode')
        self._get_coordinates_for_mode = patched_get_coordinates_for_mode.start()
        self._get_coordinates_for_mode.return_value = sentinel.coordinates

        self.addCleanup(patched_get_coordinates_for_mode.stop)

    def test_coordinates(self):
        """Should call _get_coordinates_for_mode and return result in place"""

        country = self.StubCountry

        result = format_area_data(country)

        self._get_coordinates_for_mode.assert_called_once_with(None, country, None)
        self.assertIs(sentinel.coordinates, result['geometry']['coordinates'])

    def test_result_without_continent(self):
        """Should return country information if continent is not provided"""

        country = self.StubCountry
        expected_result = {
            'type': 'Feature',
            'properties': {'name': sentinel.country_name, 'id': sentinel.country_id},
            'geometry': {'type': 'MultiPolygon', 'coordinates': sentinel.coordinates},
        }

        result = format_area_data(country)

        self.assertEqual(expected_result, result)

    def test_result_with_continent(self):
        """Should return continent information if continent is provided"""

        country = self.StubCountry
        continent = self.StubContinent
        expected_result = {
            'type': 'Feature',
            'properties': {'name': sentinel.continent_name, 'id': sentinel.continent_id},
            'geometry': {'type': 'MultiPolygon', 'coordinates': sentinel.coordinates},
        }

        result = format_area_data(country, continent=continent)

        self.assertEqual(expected_result, result)


class TestAsJson(TestCase):
    @patch('application.formatters.jsonify')
    def test_expected_call(self, patched_jsonify):
        """Should call 'jsonify' with the correct input"""
        expected_call = {'type': 'FeatureCollection', 'features': sentinel.data}

        as_json(sentinel.data)

        patched_jsonify.assert_called_once_with(expected_call)

    @patch('application.formatters.jsonify', return_value=sentinel.result)
    def text_result(self):
        """Should return result directly from jsonify"""
        result = as_json(sentinel.data)

        self.assertIs(sentinel.result, result)
