# -*- coding: utf-8 -*-
from app.config import db_sql
from flask import render_template
# from datetime import datetime
# from app.utils import key_utils
from flask_login import current_user
from app.models import Lugares_Usuarios


class UsuarioLugar(object):
    def __init__(self, usuario, lugar):
        self.usuario = usuario
        self.lugar = lugar

    def generate_token(self, lugar):
        pass


def generar_qr_lugar(id):
    if current_user.is_authenticated:
        lugar_usuario = db_sql.session.query(Lugares_Usuarios).filter(
            Lugares_Usuarios.id_lugar == id,
            Lugares_Usuarios.id_usuario == current_user.id
        )
        # print(lugar_usuario.first())
        return render_template('index.html')
