# -*- coding: utf-8 -*-
from flask import Blueprint
from app.modules.Lugar import check_lugar


mod_lugar = Blueprint('check_lugar',
                      __name__,
                      url_prefix='/lugar')


mod_lugar.add_url_rule('/enlace_lugar',
                       view_func=check_lugar.enlace_lugar,
                       methods=['GET', 'POST'])

mod_lugar.add_url_rule('/actualizar_llave_lugar/<id>',
                       view_func=check_lugar.actualizar_llave_lugar)
