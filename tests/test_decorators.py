from unittest import TestCase

from application import app
from application.decorators import as_feature_collection


class BasicTests(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False


class TestAsFeatureCollection(BasicTests):
    def test_calls_decorated_function(self):
        with app.app_context():
            @as_feature_collection
            def stub_function():
                return 'STUB_STRING'

            result = stub_function()

            self.assertEqual('STUB_STRING', result)
