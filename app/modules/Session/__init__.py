from app.config import db_sql
from app.models import Detalle_registro, Registro, Lugar, Computadora


def get_lugares_activos(id_user):
    lugar_activo = db_sql.session.query(
            Lugar.nombre, Lugar.id, Registro.fecha_hora_entrada
        ).join(
            Registro
        ).filter(
            (Registro.id_usuario == id_user) &
            (Registro.fecha_hora_salida.is_(None))
        )
    return [{'id': i.id,
             'nombre': i.nombre,
             'fecha_hora_entrada': i.fecha_hora_entrada}
            for i in lugar_activo.all()]


def get_recursos_activos(id_user):
    recursos = db_sql.session.query(Detalle_registro).filter(
        Detalle_registro.fecha_hora_entrega.is_(None)
    ).join(Registro.detalles_registro_salida).filter(
        Registro.id_usuario == id_user
    ).join(Computadora, Lugar)

    return [{'Detalle_registro': i.serialize,
             'Computadora': i.Computadora.serialize,
             'Registro': i.Registro_salida.serialize,
             'Lugar': i.Registro.Lugar.serialize,
             }
            for i in recursos.all()]
