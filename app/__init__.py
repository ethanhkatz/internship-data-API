import flask

app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

import app.routes.hotel_predictions
