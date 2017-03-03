# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.config import db_sql
from flask import request, flash, render_template, url_for, redirect, \
                  Blueprint, Markup
from datetime import datetime
from app.utils import key_utils
from flask_security import url_for_security
from flask_login import current_user
from app.models import Lugar, Usuario, Registro, Detalle_registro


class check_lugar_form(FlaskForm):
    codigo = StringField(u'Código', validators=[DataRequired()])
    nip = PasswordField(u'Nip', validators=[DataRequired()])
    submit = SubmitField(label="Check")


mod_lugar = Blueprint('check_lugar', __name__, url_prefix='/lugar')


class CheckLugar(object):
    """
    Clase que encapsula el manejo de entradas y salidas de un Lugar.
    :param id_lugar: id del lugar en donde se quiere registrar el evento
    :type id_lugar: int
    :param key: Llave para verificar si el acceso al lugar es válido
    :type key: string
    """
    def __init__(self, id_lugar, key):
        self.id_lugar = int(id_lugar)
        self.key = str(key)
        self.lugar = None
        self.usuario = None
        self.lugar_activo = None

        self.obten_lugar()

    def set_usuario(self, usuario):
        """
        Configura un usuario para después ser usado por otros métodos
        :param usuario:
        :type usuario: app.models.Usuario
        """
        self.usuario = usuario

    def obten_lugar(self):
        """
        Si existe un Lugar con ese id y esa llave, entonces guarda en
        self.lugar el objeto Lugar y lo retorna. Si no existe el lugar entonces
        guardará y retornará None.
        :return: app.models.Lugar
        """
        query = db_sql.session.query(Lugar.id, Lugar.nombre).filter(
            (Lugar.id == self.id_lugar) & (Lugar.key == str(self.key))
        )
        if query.count() > 0:
            self.lugar = query.first()
        else:
            self.lugar = None
        return self.lugar

    def lugar_valido(self):
        """
        Retorna si ya está seteado un lugar válido en el objeto self o no.
        :return: bool
        """
        return self.lugar is not None

    def obten_lugar_activo(self):
        """
        Obtiene el lugar donde el usuario guardado en self.usuario está activo.
        En caso de que no tenga un lugar activo retornará None.
        En caso de que no exista un usuario en self.usuario arrojará una
        excepción
        :return: app.models.Registro
        :raises: ValueError
        """
        if self.lugar_activo is None:
            if self.usuario is None:
                raise ValueError("self.usuario no ha sido definido, primero llama \
                                  a self.set_usuario")
            else:
                lugar_activo = db_sql.session.query(Registro).filter(
                    (Usuario.id == self.usuario.id) &
                    (Registro.fecha_hora_salida.is_(None))
                )
                if(lugar_activo.count() > 0):
                    self.lugar_activo = lugar_activo.first()
                else:
                    self.lugar_activo = None
                return self.lugar_activo
        else:
            return self.lugar_activo

    def registra_entrada(self):
        """
        Registra la entrada del usuario guardado en self.usuario en el lugar
        self.lugar
        En caso de que no exista un usuario guardado en self.usuario o un lugar
        guardado en self.lugar arrojará una excepción.
        :raises: ValueError
        """
        if self.usuario is None:
            raise ValueError("self.usuario no ha sido definido, primero llama \
                              a self.set_usuario")
        elif self.lugar is None:
            raise ValueError("self.lugar no ha sido definido, primero llama \
                              a self.obten_lugar")
        else:
            self.obten_lugar_activo()
            if self.lugar_activo is None:
                entrada = Registro(id_usuario=self.usuario.id,
                                   id_lugar=self.lugar.id)
                db_sql.session.add(entrada)
                db_sql.session.commit()
            else:
                # TODO sólo permite hacer entradas extras si la entrada previa
                # fue realizada en el lugar padre de este lugar
                raise ValueError("El usuario ya está activo en otro lugar")

    def registra_salida(self):
        """
        Registra la salida del usuario guardado en self.usuario en el lugar
        self.lugar_activo
        En caso de que no exista un lugar guardado en self.lugar_activo
        arrojará una excepción.
        :raises: ValueError
        """
        if self.lugar_activo is None:
            raise ValueError("self.lugar_activo no ha sido definido, primero \
                              llama a self.obten_lugar_activo")
        else:
            self.lugar_activo.fecha_hora_salida = datetime.utcnow()
            db_sql.session.commit()

    def computadora_activa(self):
        """
        Retorna True si existe una computadora activa asociada al usuario
        guardado en self.usuario
        En caso de que no exista un usuario guardado en self.usuario o un lugar
        guardado en self.lugar arrojará una excepción.
        :return: bool
        :raises: ValueError
        """
        if self.usuario is None:
            raise ValueError("self.usuario no ha sido definido, primero llama \
                              a self.set_usuario")
        else:
            c_activa = db_sql.session.query(Detalle_registro.id).filter(
                (Detalle_registro.fecha_hora_toma.isnot(None)) &
                (Detalle_registro.fecha_hora_entrega.is_(None))
            ).join(Registro).filter(
                (Registro.id_usuario == self.usuario.id) &
                (Registro.fecha_hora_salida.is_(None))
            )
            return c_activa.count() > 0

    def valida_salida(self):
        """
        Valida que se pueda crear una salida para el usuario guardado en
        self.usuario del lugar guardado en self.lugar_activo
        :return: bool, {:text: string, :category: string}
        """
        if(self.lugar_activo.id_lugar == int(self.id_lugar)):
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
        """
        Valida que se pueda crear una entrada para el usuario guardado en
        self.usuario del lugar guardado en self.lugar_activo
        :return: bool, {:text: string, :category: string}
        """
        self.lugar_activo = self.obten_lugar_activo()
        if(self.lugar_activo is None):
            self.registra_entrada()
            return True, {'text': u'Usuario con código: ' + self.usuario.codigo
                          + u' entró a ' + self.lugar.nombre,
                          'category': 'success'}
        else:
            return self.valida_salida()

    def usuario_valido(self, codigo, nip):
        """
        Valida que exista un usuario que cumpla con el par codigo / nip
        :param codigo: El código del usuario
        :type codigo: string
        :param nip: El nip del usuario
        :type nip: string
        :return: bool, {:text: string, :category: string}
        """
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
            if 'admin' in current_user.roles:
                flash(Markup(u'Te encuentras como Admin, favor de copiar la \
                             url, <a href="' + url_for_security('logout') +
                             u'">cerrar sesión</a> y volver a usar la URL'),
                      category='danger')
                return render_template('enlace_lugar.html',
                                       id=id_lugar,
                                       key=key,
                                       nombre=check_lugar.lugar.nombre,
                                       form=formulario)
            else:
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
