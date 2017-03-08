# -*- coding: utf-8 -*-
from app.config import db_sql
from flask import render_template, flash
# from datetime import datetime
# from app.utils import key_utils
from flask_login import current_user
from app.models import Lugares_Usuarios, Lugar
from CheckLugar import CheckLugar


class CheckLugarDinamico(CheckLugar):
    def __init__(self, id_lugar, usuario, key_dinamico):
        self.key_dinamico = key_dinamico
        self.set_usuario(usuario)
        CheckLugar.__init__(self, id_lugar=id_lugar)
        self.obten_lugar()

    def obten_lugar(self):
        """
        Si existe un Lugar con ese id y esa llave dinámica, entonces guarda en
        self.lugar el objeto Lugar y lo retorna. Si no existe el lugar entonces
        guardará y retornará None.
        :return: app.models.Lugar
        """
        lugar_usuario = db_sql.session.query(Lugares_Usuarios).filter(
            Lugares_Usuarios.id_lugar == self.id_lugar,
            Lugares_Usuarios.id_usuario == self.usuario.id,
            Lugares_Usuarios.token == self.key_dinamico
        )
        if lugar_usuario.count() > 0:
            query = db_sql.session.query(Lugar.id, Lugar.nombre).filter(
                (Lugar.id == self.id_lugar)
            )
            self.lugar = query.first()
        else:
            self.lugar = None
        return self.lugar


def generar_qr_lugar(id):
    if current_user.is_authenticated:
        lugar_usuario = db_sql.session.query(Lugares_Usuarios).filter(
            Lugares_Usuarios.id_lugar == id,
            Lugares_Usuarios.id_usuario == current_user.id
        )
        if(lugar_usuario.first()):
            flash(u'Sí tienes permisos para generar QR de este lugar',
                  category='warning')
            return render_template('index.html')
        else:
            flash(u'No tienes permisos para generar QR de este lugar',
                  category='warning')
            return render_template('index.html')
