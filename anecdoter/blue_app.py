from flask import Blueprint

blue = Blueprint('main', __name__)

from . import views