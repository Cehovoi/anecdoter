import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = 'mysecret' #os.environ.get('mysecret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI') or \
    #     f'postgresql://zhenyavo:{os.environ.get("PASSWORD")}@localhost/jokes_peeper'
    SQLALCHEMY_DATABASE_URI = 'postgresql://zhenyavo:dun5k466@localhost/jokes_peeper'