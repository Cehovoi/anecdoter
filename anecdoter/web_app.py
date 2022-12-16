import os


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
admin = Admin()
login = LoginManager()
login.session_protection = 'strong'
login.login_view = 'auth.login'
folder = os.path.dirname(os.path.abspath(__file__)) + '/static'


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.getenv('CONFIG'))
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    login.init_app(app)
    from . blue_app import blue as main_blueprint
    from . auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app

# app = create_app()