# -*- coding: utf-8 -*-
from app.config import db_sql
from sqlalchemy import and_
from app.models import Usuario, Registro, Detalle_registro


class tiempo(object):
    """
    docstring for .
    """
    def __init__(self, id_registro, fecha_hora_entrada):
        self.id_registro = int(id_registro)
        self.fecha_hora_entrada = fecha_hora_entrada

    def obten_entradas(self):
        """
        Obtiene el maximo de entradas
        """
        if self.usuario is None:
            raise ValueError("self.usuario no ha sido definido, primero llama \
                              a self.set_usuario")
        if self.usuario is 'admin':
            entradas = db_sql.session.query(Registro).filter and_(
                Registro.fecha_hora_entrada <= '2017-03-10',
                Registro.fecha_hora_entrada >= '2017-03-10')
            return entradas  # revisar
