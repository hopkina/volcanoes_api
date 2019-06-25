from functools import wraps

from application.formatters import as_json


def as_feature_collection(func):
    @wraps
    def wrapped_view(*args, **kwargs):
        data = func(*args, **kwargs)
        return as_json(data)

    return wrapped_view
