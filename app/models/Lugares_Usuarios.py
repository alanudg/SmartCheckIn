from app.db import db_sql as db
from app.utils.key_utils import generate_key
from datetime import datetime


class Lugares_Usuarios(db.Model):
    __tablename__ = 'lugares_usuarios'
    id_usuario = db.Column(db.Integer(),
                           db.ForeignKey('usuario.id'),
                           primary_key=True)
    id_lugar = db.Column(db.Integer(),
                         db.ForeignKey('lugar.id'),
                         primary_key=True)

    fecha_hora_token = db.Column(db.DateTime,
                                 nullable=False,
                                 default=datetime.utcnow)
    token = db.Column(db.String(15), default=generate_key)

    # lugar = db.relationship('Lugar',
    #                         backref="usuarios_asignados")
    # usuario = db.relationship('Usuario',
    #                           backref="lugares_asignados")

    def __unicode__(self):
        return str(self.lugar.nombre)

    def __hash__(self):
        return hash(str(self.lugar.nombre))
