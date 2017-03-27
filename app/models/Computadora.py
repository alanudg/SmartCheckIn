# -*- coding: utf-8 -*-
from app.config import db_sql as db
from app.utils.key_utils import generate_key


class Computadora(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    key = db.Column(db.String(15), default=generate_key)
    nombre = db.Column(db.String, nullable=False)
    disponible = db.Column(db.Boolean, default=True)

    id_lugar = db.Column(db.Integer, db.ForeignKey('lugar.id'), nullable=False)

    detalles_registro = db.relationship('Detalle_registro',
                                        backref='Computadora', lazy=True)

    def __unicode__(self):
        return self.nombre

    def __hash__(self):
        return hash(self.nombre)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'key': self.key,
            'nombre': self.nombre,
            'disponible': self.disponible,
        }
