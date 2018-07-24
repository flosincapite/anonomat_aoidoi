import flask
import flask_bootstrap

wsgi_app = flask.Flask(__name__)
bootstrap = flask_bootstrap.Bootstrap(wsgi_app)

from app import routes
