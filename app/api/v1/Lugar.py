from flask import jsonify, abort
from app.config import db_sql
from app.models import Lugar


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
    try:
        id = int(id)
    except:
        return abort(400)

    lugares = db_sql.session.query(Lugar).filter(
        Lugar.id == id
    )
    if(lugares.count()):
        return jsonify(lugares.first().serialize)
    else:
        return abort(404)
