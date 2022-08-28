import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://zhenyavo:dun5k466@localhost/jokes_peeper'


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('LOGIN')}:{os.environ.get('PASSWORD')}@ec2-34-248-169-69.eu-west-1.compute.amazonaws.com:5432/dd8208nm4umc0i"