import flask

app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

from .routes.healthcheck import healthcheck
from .routes.hotel_predictions import hotel_predictions
