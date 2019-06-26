from application.formatters import as_json


def as_feature_collection(func):
    def wrapped_view(*args, **kwargs):
        data = func(*args, **kwargs)
        return as_json(data)

    wrapped_view.__name__ = func.__name__
    return wrapped_view
