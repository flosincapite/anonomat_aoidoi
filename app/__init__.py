import flask
# import flask_cors
import flask_login
# import flask_bootstrap

from app import blog_post
from app import config 
from app import regex_converter
from app.login import user
from util import database


wsgi_app = flask.Flask(__name__)
# _ = flask_cors.CORS(wsgi_app)
wsgi_app.config.from_object(config.Config)
# bootstrap = flask_bootstrap.Bootstrap(wsgi_app)


blog_db = database.YamlDatabase(
    wsgi_app.config['BLOG_DIRECTORY'], blog_post.BlogPost)


user_db = database.YamlDatabase(
    wsgi_app.config['USER_DIRECTORY'], user.User, key_func=lambda u: u.name)


login_manager = flask_login.LoginManager()
login_manager.init_app(wsgi_app)


wsgi_app.url_map.converters['re'] = regex_converter.RegexConverter


from app import routes
