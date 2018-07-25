import flask
# import flask_bootstrap

from app import config 


wsgi_app = flask.Flask(__name__)
wsgi_app.config.from_object(config.Config)
# bootstrap = flask_bootstrap.Bootstrap(wsgi_app)

from app import routes
