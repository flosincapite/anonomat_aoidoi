import sqlite3

import flask
# import flask_cors
import flask_login
# import flask_bootstrap

from app import blog_post
from app import config 
from app import regex_converter
from app.login import user


wsgi_app = flask.Flask(__name__)
# _ = flask_cors.CORS(wsgi_app)
wsgi_app.config.from_object(config.Config)
# bootstrap = flask_bootstrap.Bootstrap(wsgi_app)

wsgi_app.logger.error(f'DATABASE is {wsgi_app.config["DATABASE"]}')

# check_same_thread unnecessary because we only read from this database.
db = sqlite3.connect(wsgi_app.config['DATABASE'], check_same_thread=False)


login_manager = flask_login.LoginManager()
login_manager.init_app(wsgi_app)


wsgi_app.url_map.converters['re'] = regex_converter.RegexConverter


from app import routes
