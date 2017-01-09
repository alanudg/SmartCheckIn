from app.config import db_sql as db


class Computadora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lugar_id = db.Column(db.Integer, db.ForeignKey('lugar.id'),
                         nullable=False)
    nombre = db.Column(db.String, nullable=False)
    registro_id = db.relationship('Registro', backref='Computadora', lazy=True)

    def __unicode__(self):
        return self.nombre

    def __hash__(self):
        return hash(self.nombre)
