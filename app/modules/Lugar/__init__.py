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


class check_lugar_form(FlaskForm):
    codigo = StringField(u'Código', validators=[DataRequired()])
    nip = PasswordField(u'Nip', validators=[DataRequired()])
    submit = SubmitField(label="Check")


mod_lugar = Blueprint('check_lugar', __name__, url_prefix='/lugar')


class CheckLugar():
    def __init__(self, id_lugar, key):
        self.id_lugar = int(id_lugar)
        self.key = str(key)
        self.lugar = None
        self.usuario = None
        self.lugar_activo = None

        self.obten_lugar()

    def set_usuario(self, usuario):
        self.usuario = usuario

    def obten_lugar(self):
        query = db_sql.session.query(Lugar.id, Lugar.nombre).filter(
            (Lugar.id == self.id_lugar) & (Lugar.key == str(self.key))
        )
        if query.count() > 0:
            self.lugar = query.first()
        else:
            self.lugar = None

    def lugar_valido(self):
        return self.lugar is not None

    def obten_lugar_activo(self):
        lugar_activo = db_sql.session.query(Registro).filter(
            (Usuario.id == self.usuario.id) &
            (Registro.activo) &
            (Registro.tipo_registro_id == config.ID_ENTRADA_LUGAR)
        )
        if(lugar_activo.count() > 0):
            return lugar_activo.first()

    def registra_entrada(self):
        entrada = Registro(usuario_id=self.usuario.id,
                           lugar_id=self.lugar.id,
                           tipo_registro_id=config.ID_ENTRADA_LUGAR,
                           activo=True)
        db_sql.session.add(entrada)
        db_sql.session.commit()

    def registra_salida(self):
        self.lugar_activo.activo = False
        salida = Registro(usuario_id=self.usuario.id,
                          lugar_id=self.lugar.id,
                          tipo_registro_id=config.ID_SALIDA_LUGAR,
                          activo=False)
        db_sql.session.add(salida)
        db_sql.session.commit()

    def computadora_activa(self):
        c_activa = db_sql.session.query(Registro).filter(
            (Usuario.id == self.usuario.id) &
            (Registro.activo) &
            (Registro.tipo_registro_id == config.ID_TOMA_COMPUTADORA)
        )
        return c_activa.count() > 0

    def valida_salida(self):
        if(self.lugar_activo.lugar_id == int(self.id_lugar)):
            if(self.computadora_activa()):
                return False, {'text': u'Tienes una computadora sin entregar',
                               'category': 'warning'}
            else:
                self.registra_salida()
                return True, {'text': u'Usuario con código: ' +
                              self.usuario.codigo + u' salió de ' +
                              self.lugar.nombre,
                              'category': 'success'}
        else:
            # TODO verificar si el lugar al que quiere entrar es "hijo" del
            # lugar donde se encuentra activo
            return False, {'text': u'Tienes una entrada activa en otro lugar',
                           'category': 'warning'}

    def valida_entrada_salida_lugar(self):
        self.lugar_activo = self.obten_lugar_activo()
        if(self.lugar_activo is None):
            self.registra_entrada()
            return True, {'text': u'Usuario con código: ' + self.usuario.codigo
                          + u' entró a ' + self.lugar.nombre,
                          'category': 'success'}
        else:
            return self.valida_salida()

    def usuario_valido(self, codigo, nip):
        query = db_sql.session.query(Usuario).filter(
            (Usuario.codigo == codigo)
        )
        if(query.count() > 0):
            usuario = query.first()
            if(usuario.nip == nip):
                self.usuario = usuario
                return True, {}
            else:
                return False, {'text': u'Error en el nip del usuario',
                               'category': 'warning'}
        else:
            return False, {'text': u'No existe un usuario con el código: ' +
                           str(codigo),
                           'category': 'warning'}

    def valida_formulario(self, formulario):
        codigo = formulario.codigo.data
        nip = formulario.nip.data
        usuario_valido, res = self.usuario_valido(codigo, nip)
        if(usuario_valido):
            entrada_salida_valida, res = self.valida_entrada_salida_lugar()
        return res


@mod_lugar.route('/enlace_lugar', methods=['GET', 'POST'])
def enlace_lugar():
    key = request.args.get('key')
    id_lugar = request.args.get('id')
    check_lugar = CheckLugar(id_lugar, key)
    if check_lugar.lugar_valido():
        formulario = check_lugar_form(csrf_enabled=False)

        if current_user.is_authenticated:
            check_lugar.set_usuario(current_user)
            e, message = check_lugar.valida_entrada_salida_lugar()
            flash(message['text'], category=message['category'])
            return redirect('/')
        else:
            if formulario.validate_on_submit():
                message = check_lugar.valida_formulario(formulario)
                flash(message['text'], category=message['category'])
            # TODO Crear este template (quizás se haga un template 'padre'
            # para las vistas similares a esta)
            return render_template('enlace_lugar.html',
                                   id=id_lugar,
                                   key=key,
                                   nombre=check_lugar.lugar.nombre,
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
