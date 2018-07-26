import flask
import flask_cors
# import flask_bootstrap

from app import config 
from app import regex_converter


wsgi_app = flask.Flask(__name__)
# _ = flask_cors.CORS(wsgi_app)
wsgi_app.config.from_object(config.Config)
# bootstrap = flask_bootstrap.Bootstrap(wsgi_app)


wsgi_app.url_map.converters['re'] = regex_converter.RegexConverter


from app import routes
