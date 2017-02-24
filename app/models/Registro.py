from app.config import db_sql as db
from datetime import datetime


class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    fecha_hora_entrada = db.Column(db.DateTime, nullable=False,
                                   default=datetime.utcnow)
    fecha_hora_salida = db.Column(db.DateTime, nullable=True)
    fecha_hora_toma = db.Column(db.DateTime, nullable=True)
    fecha_hora_entrega = db.Column(db.DateTime, nullable=True)

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)
    id_lugar = db.Column(db.Integer, db.ForeignKey('lugar.id'),
                         nullable=False)
    id_computadora = db.Column(db.Integer, db.ForeignKey('computadora.id'))

    def __unicode__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Registro %r | %r>' % self.id, self.id_usuario
