# -*- coding: utf-8 -*-
from app.config import db_sql
from flask import render_template, flash, request, redirect
# from datetime import datetime
# from app.utils import key_utils
from flask_login import current_user
from app.models import Lugares_Usuarios, Lugar, Usuario
from CheckLugar import CheckLugar
from app.utils.key_utils import generate_key
from datetime import datetime


class CheckLugarDinamico(CheckLugar):
    def __init__(self, id_lugar, id_usuario, key_dinamico):
        self.key_dinamico = key_dinamico
        self.set_usuario(id_usuario)
        CheckLugar.__init__(self, id_lugar=id_lugar, usuario=self.usuario)
        self.obten_lugar()

    def set_usuario(self, usuario_id):
        usuario = db_sql.session.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.active
        )
        self.usuario = usuario.first()

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
            lugar_usuario = lugar_usuario.first()
            fmt = '%Y-%m-%d %H:%M:%S'
            d1 = datetime.strptime(
                        lugar_usuario.
                        fecha_hora_token.strftime("%Y-%m-%d %H:%M:%S"),
                        fmt)
            delta = (datetime.utcnow()-d1).seconds
            # TODO cambiar este valor de 120 por un valor en el archivo de
            # configuración
            if(delta <= 120):
                query = db_sql.session.query(Lugar.id, Lugar.nombre).filter(
                    (Lugar.id == self.id_lugar)
                )
                self.lugar = query.first()
            else:
                self.lugar = None
        else:
            self.lugar = None
        return self.lugar


def generar_qr_lugar(id):
    if current_user.is_authenticated:
        lugar_usuario = db_sql.session.query(Lugares_Usuarios).filter(
            Lugares_Usuarios.id_lugar == id,
            Lugares_Usuarios.id_usuario == current_user.id
        )
        lugar_usuario = lugar_usuario.first()
        if(lugar_usuario):
            lugar_usuario.token = generate_key()
            lugar_usuario.fecha_hora_token = datetime.utcnow()
            db_sql.session.commit()
            lugar = db_sql.session.query(Lugar.nombre).filter(
                Lugar.id == lugar_usuario.id_lugar
            )
            return render_template('lugar/enlace_lugar_dinamico.html',
                                   id_lugar=lugar_usuario.id_lugar,
                                   id_usuario=lugar_usuario.id_usuario,
                                   token=lugar_usuario.token,
                                   nombre=lugar.first().nombre)
        else:
            flash(u'No tienes permisos para generar QR de este lugar',
                  category='warning')
            return redirect('/')
    else:
        flash(u'Necesitas iniciar sesión para hacer esta acción',
              category='warning')
        return redirect('/')


def enlace_lugar_dinamico():
    id_lugar = request.args.get('id_lugar')
    id_usuario = request.args.get('id_usuario')
    token = request.args.get('token')

    dinamico = db_sql.session.query(Lugares_Usuarios).filter(
        Lugares_Usuarios.id_lugar == id_lugar,
        Lugares_Usuarios.id_usuario == id_usuario,
        Lugares_Usuarios.token == token,
    )

    if(dinamico.first() and current_user.has_role('admin')):
        lugar_usuario = dinamico.first()
        check_lugar_dinamico = CheckLugarDinamico(
                                id_lugar=lugar_usuario.id_lugar,
                                id_usuario=lugar_usuario.id_usuario,
                                key_dinamico=lugar_usuario.token)

        try:
            e, message = check_lugar_dinamico.valida_entrada_salida_lugar()
            flash(message['text'], category=message['category'])
            return redirect('/')
        except Exception:
            flash(u'Tu token para ese lugar caducó, genera uno nuevo',
                  category='warning')
            return redirect('/')
    else:
        flash(u'No tienes permisos para realizar esa acción',
              category='warning')
        return redirect('/')
