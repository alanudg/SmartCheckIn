from app.config import db_sql as db
from datetime import datetime
from app.models.Detalle_registro import Detalle_registro


class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    fecha_hora_entrada = db.Column(db.DateTime, nullable=False,
                                   default=datetime.utcnow)
    fecha_hora_salida = db.Column(db.DateTime, nullable=True)

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)
    id_lugar = db.Column(db.Integer, db.ForeignKey('lugar.id'),
                         nullable=False)
    detalles_registro = db.relationship('Detalle_registro',
                                        backref='Registro',
                                        primaryjoin=id==Detalle_registro.id_registro_entrada
                                        )
    detalles_registro_salida = db.relationship('Detalle_registro',
                                               backref='Registro_salida',
                                               primaryjoin=id==Detalle_registro.id_registro_salida
                                               )

    def __unicode__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Registro %r | %r>' % self.id, self.id_usuario
