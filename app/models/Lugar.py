from app.config import db_sql as db
from geoalchemy2.types import Geometry


class Lugar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True)
    coordenadas = db.Column(Geometry("POLYGON"))
    hora_apertura = db.Column(db.Time)
    hora_cierre = db.Column(db.Time)
    computadora = db.relationship('Computadora', backref='Lugar', lazy=True)

    def __unicode__(self):
        return self.nombre

    def __hash__(self):
        return hash(self.nombre)
