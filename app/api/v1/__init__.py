from flask import Blueprint
from flask_security import login_required
from app.api.v1 import Lugar as Lugar

mod_api = Blueprint('api/v1',
                    __name__,
                    url_prefix='/api/v1')

mod_api.add_url_rule('/lugares',
                     view_func=login_required(Lugar.get_lugares),
                     methods=['GET'])

mod_api.add_url_rule('/lugares/<id>',
                     view_func=login_required(Lugar.get_lugar),
                     methods=['GET'])
