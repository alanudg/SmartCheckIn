# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from flask_security import login_required
from app.config import db_sql
from app.models import Lugar, Usuario, Registro, Detalle_registro


mod_api = Blueprint('api/v1',
                    __name__,
                    url_prefix='/api/v1')


@mod_api.route('/lugares', methods=['GET'])
@login_required
def get_lugares():
    """
    @api {get} /lugares/:id Obtiene una lista de lugares
    @apiVersion 1.0.0
    @apiName get_lugares
    @apiGroup Lugar
    @apiDescription Obtiene una lista de lugares
    @apiExample Example usage:
    curl -i http://localhost/api/lugares
    @apiSuccess {Object}    Lugares                 La lista de lugares.
    @apiSuccess {String}    Lugares.id              Id del lugar.
    @apiSuccess {String}    Lugares.coordenadas     Coordenadas del lugar
    @apiSuccess {String}    Lugares.nombre          El nombre del lugar
    @apiError UserNotFound      The <code>id</code> of the User was not found.
    """
    lugares = db_sql.session.query(Lugar).filter(
        # Lugar.nombre == 'Otro'
    )
    return jsonify([i.serialize for i in lugares.all()])


@mod_api.route('/lugares/<id>', methods=['GET'])
@login_required
def get_lugar(id):
    """
    @api {get} /lugares/:id Obtiene una lista de lugares
    @apiVersion 1.0.0
    @apiName get_usuario
    @apiGroup Usuario
    @apiDescription Obtiene una lista de lugares
    @apiExample Example usage:
    curl -i http://localhost/api/lugares
    @apiSuccess {Object}    Lugar                 La lista de lugares.
    @apiSuccess {String}    Lugar.id              Id del lugar.
    @apiSuccess {String}    Lugar.coordenadas     Coordenadas del lugar
    @apiSuccess {String}    Lugar.nombre          El nombre del lugar
    @apiError UserNotFound      The <code>id</code> of the User was not found.
    """
    lugares = db_sql.session.query(Lugar).filter(
        Lugar.id == id
    )
    if(lugares.count()):
        return jsonify(lugares.first().serialize)
    else:
        return jsonify({'error': 404})

# mod_api.add_url_rule('/enlace_lugar',
#                      view_func=check_lugar.enlace_lugar,
#                      methods=['GET', 'POST'])
