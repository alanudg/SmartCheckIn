# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.config import db_sql
from flask import request, flash, render_template, url_for, redirect, Markup, \
                  session
from app.utils import key_utils
from flask_security import url_for_security
from flask_login import current_user
from app.models import Lugar
from CheckLugar import CheckLugar


class check_lugar_form(FlaskForm):
    codigo = StringField(u'Código', validators=[DataRequired()])
    nip = PasswordField(u'Nip', validators=[DataRequired()])
    submit = SubmitField(label="Check")


def enlace_lugar():
    key = request.args.get('key')
    id_lugar = request.args.get('id')
    check_lugar = CheckLugar(id_lugar, key)
    if check_lugar.lugar_valido():
        formulario = check_lugar_form(csrf_enabled=False)

        if current_user.is_authenticated:
            if 'admin' in current_user.roles:
                flash(Markup(u'Te encuentras como Admin, favor de copiar la \
                             url, <a href="' + url_for_security('logout') +
                             u'">cerrar sesión</a> y volver a usar la URL'),
                      category='danger')
                return render_template('lugar/enlace_lugar.html',
                                       id=id_lugar,
                                       key=key,
                                       nombre=check_lugar.lugar.nombre,
                                       form=formulario)
            else:
                check_lugar.set_usuario(current_user)
                e, message = check_lugar.valida_entrada_salida_lugar()
                if(e):
                    if(check_lugar.registro_entrada is not None):  # Checkin
                        lugar_activo = db_sql.session.query(Lugar).filter(
                            Lugar.id == id_lugar
                        )
                        lugar_activo = lugar_activo.first()
                        ent = check_lugar.registro_entrada
                        session['l_act'].append({
                            'id': lugar_activo.id,
                            'nombre': lugar_activo.nombre,
                            'fecha_hora_entrada': ent.fecha_hora_entrada
                        })
                    else:  # Checkout
                        session['l_act'] = [x for x in session['l_act']
                                            if not
                                            int(x['id']) == int(id_lugar)]
                flash(message['text'], category=message['category'])
                return redirect('/')
        else:
            if formulario.validate_on_submit():
                message = check_lugar.valida_formulario(formulario)
                flash(message['text'], category=message['category'])
            # TODO Crear este template (quizás se haga un template 'padre'
            # para las vistas similares a esta)
            return render_template('lugar/enlace_lugar.html',
                                   id=id_lugar,
                                   key=key,
                                   nombre=check_lugar.lugar.nombre,
                                   form=formulario)
    else:
        flash(u'Error de acceso: '+str(id_lugar))
    return redirect('/')


def actualizar_llave_lugar(id):
    # TODO: Verificar si el usuario tiene permisos sobre este lugar
    if current_user.has_role('admin'):
        db_sql.session.query(Lugar.id).filter(
            (Lugar.id == id)
        ).update(
            {'key': key_utils.generate_key()}
        )
        db_sql.session.commit()
        flash(u'Se actualizó el lugar con id: '+str(id))
        return redirect(
                url_for('lugar.index_view') + '?' + '&'.join(request.args)
                )
    else:
        flash(u'No tienes los permisos necesarios para realizar esa acción')
        # FIXME: no es index, se tiene que crear una vista general
        return redirect('/')
