from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import urandom
import logging


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/identitySync'
    app.config['SQLALCHEMY_BINDS'] = {'usko': 'mysql+pymysql://root:root@localhost/usko'}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = "very_very_secret" #urandom(16)

    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message = 'Pre prístup na túto stránku je nutné sa prihlásiť.'
    login_manager.init_app(app)

    # from is_models.is_models import Ldapexport

    return app
