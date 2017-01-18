from app.config import db_sql as db
from datetime import datetime


class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)
    lugar_id = db.Column(db.Integer, db.ForeignKey('lugar.id'),
                         nullable=False)

    tipo_registro_id = db.Column(db.Integer,
                                 db.ForeignKey('tipo_registro.id'),
                                 nullable=False)

    # Puede no pertenecer al registro de una computadora porque puede ser
    # el registro de una entrada/salida
    computadora_id = db.Column(db.Integer, db.ForeignKey('computadora.id'))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)

    def __unicode__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Registro %r | %r>' % self.id, self.usuario_id
