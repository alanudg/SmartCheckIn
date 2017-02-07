# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.config import db_sql
from flask import request, flash, render_template, url_for, redirect, Blueprint
from app import config
from app.utils import key_utils
from flask_login import current_user
from app.models import Lugar, Usuario, Registro, Computadora


class registra_toma_deja_computadora(FlaskForm):
    codigo = StringField(u'Código', validators=[DataRequired()])
    nip = PasswordField(u'Nip', validators=[DataRequired()])
    submit = SubmitField(label="Check")


mod_computadora = Blueprint('check_computadora',
                            __name__,
                            url_prefix='/computadora')


@mod_computadora.route('/enlace_computadora', methods=['GET', 'POST'])
def enlace_computadora():
    key = request.args.get('key')
    id_computadora = request.args.get('id')
    query = db_sql.session.query(Computadora.id, Computadora.nombre).filter(
        (Computadora.id == id_lugar) & (Lugar.key == str(key))
    )
    if query.count() > 0:
        # TODO Pasar de Lugar a Computadora desde aquí hasta "EndTODO"
        computadora = query.first()
        nombre = computadora.nombre
        formulario = registra_toma_deja_computadora(csrf_enabled=False)

        if current_user.is_authenticated:
            flash(u'Evento en el lugar con id: ' + str(id_lugar) +
                  str(lugar.nombre))
        else:
            if formulario.validate_on_submit():
                codigo = formulario.codigo.data
                nip = formulario.nip.data
                usuario = db_sql.session.query(Usuario.nip, Usuario.id).filter(
                    (Usuario.codigo == codigo)
                )
                if(usuario.count() > 0):
                    usuario = usuario.first()
                    if(usuario.nip == nip):
                        lugar_activo = db_sql.session.query(Registro)\
                            .filter((Usuario.id == usuario.id) &
                                    (Registro.activo) &
                                    (Registro.tipo_registro_id ==
                                        config.ID_ENTRADA_LUGAR))
                        if(lugar_activo.count() > 0):
                            comp_activa = db_sql.session.query(Registro)\
                                .filter((Usuario.id == usuario.id) &
                                        (Registro.activo) &
                                        (Registro.tipo_registro_id ==
                                            config.ID_TOMA_COMPUTADORA))
                            if(comp_activa.count() > 0):
                                flash(u'Tienes una computadora sin entregar',
                                      category='warning')
                            else:
                                lugar_activo.first().activo = False
                                salida = Registro(usuario_id=usuario.id,
                                                  lugar_id=lugar.id,
                                                  tipo_registro_id=config.ID_SALIDA_LUGAR,
                                                  activo=False)
                                db_sql.session.add(salida)
                                db_sql.session.commit()
                                flash(u'Usuario salió de lugar',
                                      category='success')
                        else:
                            entrada = Registro(usuario_id=usuario.id,
                                               lugar_id=lugar.id,
                                               tipo_registro_id=config.ID_ENTRADA_LUGAR,
                                               activo=True)
                            db_sql.session.add(entrada)
                            db_sql.session.commit()
                            flash(u'Usuario entró a lugar',
                                  category='success')
                    else:
                        flash(u'Error en el nip del usuario',
                              category='warning')
                else:
                    flash(u'No existe un usuario con el código: ' +
                          str(codigo), category='warning')
        return render_template('enlace_lugar.html',
                               id=id,
                               key=key,
                               nombre=nombre,
                               form=formulario)
        # EndTODO Pasar de Lugar a Computadora desde aquí hasta "EndTODO"
    else:
        flash(u'Error de acceso: '+str(id_lugar))
    return render_template('index.html')


@mod_computadora.route('/actualizar_llave_computadora/<id>')
def actualizar_llave_computadora(id):
    # TODO: Verificar si el usuario tiene permisos sobre esta computadora
    if current_user.has_role('admin'):
        db_sql.session.query(Computadora.id).filter(
            (Computadora.id == id)
        ).update(
            {'key': key_utils.generate_key()}
        )
        db_sql.session.commit()
        flash(u'Se actualizó la computadora con id: '+str(id))
        return redirect(
                url_for('computadora.index_view') +
                '?' + '&'.join(request.args)
                )
    else:
        flash(u'No tienes los permisos necesarios para realizar esa acción')
        # FIXME: no es index, se tiene que crear una vista general
        return redirect('/')
