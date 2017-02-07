# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.config import db_sql
from flask import request, flash, render_template, url_for, redirect, Blueprint
from app import config
from app.utils import key_utils
from flask_login import current_user
from app.models import Lugar, Usuario, Registro


class registra_entrada_salida_lugar(FlaskForm):
    codigo = StringField(u'Código', validators=[DataRequired()])
    nip = PasswordField(u'Nip', validators=[DataRequired()])
    submit = SubmitField(label="Check")


mod_lugar = Blueprint('check_lugar', __name__, url_prefix='/lugar')


@mod_lugar.route('/enlace_lugar', methods=['GET', 'POST'])
def enlace_lugar():
    key = request.args.get('key')
    id_lugar = request.args.get('id')
    query = db_sql.session.query(Lugar.id, Lugar.nombre).filter(
        (Lugar.id == id_lugar) & (Lugar.key == str(key))
    )
    if query.count() > 0:
        lugar = query.first()
        nombre = lugar.nombre
        formulario = registra_entrada_salida_lugar(csrf_enabled=False)

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
                                # TODO ver si esto sirve o no
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
        # TODO Crear este template (quizás se haga un template 'padre' para las
        #  vistas similares a esta)
        return render_template('enlace_computadora.html',
                               id=id,
                               key=key,
                               nombre=nombre,
                               form=formulario)
    else:
        flash(u'Error de acceso: '+str(id_lugar))
    return render_template('index.html')


@mod_lugar.route('/actualizar_llave_lugar/<id>')
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
