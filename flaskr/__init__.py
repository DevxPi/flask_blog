import os
from os import environ, path
from dotenv import load_dotenv

from flask import Flask
from flask_bootstrap import Bootstrap4

BASEDIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASEDIR, ".env"))

def create_app(test_config=None):
    # create the flask instance and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'Cosmo'
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    from . import auth
    from . import blog

    bootstrap = Bootstrap4(app)
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule('/', endpoint='index')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, world!'
    
    return app