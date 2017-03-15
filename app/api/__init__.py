# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from app.config import db_sql
from app.models import Lugar, Usuario, Registro, Detalle_registro


mod_api = Blueprint('api/v1',
                    __name__,
                    url_prefix='/api/v1')


@mod_api.route('/lugares', methods=['GET'])
# @login_required
def index():
    lugares = db_sql.session.query(Lugar).filter(
        # Lugar.nombre == 'Otro'
    )
    return jsonify([i.serialize for i in lugares.all()])

# mod_api.add_url_rule('/enlace_lugar',
#                      view_func=check_lugar.enlace_lugar,
#                      methods=['GET', 'POST'])
