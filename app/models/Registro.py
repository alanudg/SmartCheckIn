from app.config import db_sql as db
import datetime


class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)
    # entrada_id
    # salida_id
    lugar_id = db.Column(db.Integer, db.ForeignKey('lugar.id'),
                         nullable=False)
    computadora_id = db.Column(db.Integer, db.ForeignKey('computadora.id'))
    # Puede no pertenecer al registro de una computadora porque puede ser
    # el registro de una entrada/salida
    fecha_hora = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __unicode__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Registro %r | %r>' % self.id, self.usuario_id
