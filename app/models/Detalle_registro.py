# -*- coding: utf-8 -*-
from app.config import db_sql as db
from datetime import datetime


class Detalle_registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    fecha_hora_toma = db.Column(db.DateTime, nullable=False,
                                default=datetime.utcnow)
    fecha_hora_entrega = db.Column(db.DateTime, nullable=True)

    id_computadora = db.Column(db.Integer, db.ForeignKey('computadora.id'),
                               nullable=False)
    id_registro_entrada = db.Column(db.Integer, db.ForeignKey('registro.id'),
                                    nullable=False)

    id_registro_salida = db.Column(db.Integer, db.ForeignKey('registro.id'),
                                   nullable=False)

    registro_entrada = db.relationship('Registro',
                                       foreign_keys=[id_registro_entrada])

    registro_salida = db.relationship('Registro',
                                      foreign_keys=[id_registro_salida])

    def __unicode__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<Detalle_registro %d | %d>' % (self.id, self.id_registro_entrada)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'fecha_hora_toma': self.fecha_hora_toma,
            'fecha_hora_entrega': self.fecha_hora_entrega,
        }
