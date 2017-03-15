from app.config import db_sql as db
from app.utils.key_utils import generate_key
from geoalchemy2.types import Geometry


class Lugar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True)
    asignacion_automatica = db.Column(db.Boolean, nullable=False,
                                      default=False)
    coordenadas = db.Column(Geometry("POLYGON"))
    key = db.Column(db.String(15), default=generate_key)
    hora_apertura = db.Column(db.Time)
    hora_cierre = db.Column(db.Time)
    privado = db.Column(db.Boolean, nullable=False, default=False)

    id_lugar_padre = db.Column(db.Integer, db.ForeignKey('lugar.id'),
                               nullable=True)

    computadoras = db.relationship('Computadora', backref='Lugar', lazy=True)
    lugar_padre = db.relationship('Lugar', remote_side=[id])
    registros = db.relationship('Registro', backref='Lugar', lazy=True)
    usuarios = db.relationship("Usuario",
                               secondary='lugares_usuarios')

    def __unicode__(self):
        return self.nombre

    def __hash__(self):
        return hash(self.nombre)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'coordenadas': str(self.coordenadas)
        }
