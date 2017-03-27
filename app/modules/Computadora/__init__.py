# -*- coding: utf-8 -*-
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.config import db_sql
from flask import request, flash, render_template, url_for, redirect,\
                  Blueprint, Markup, session
from app.utils import key_utils
from flask_login import current_user
from flask_security import url_for_security
from app.models import Lugar, Usuario, Registro, Computadora, Detalle_registro
from app.modules.Session import get_recursos_activos
from datetime import datetime


class check_comp_form(FlaskForm):
    codigo = StringField(u'Código', validators=[DataRequired()])
    nip = PasswordField(u'Nip', validators=[DataRequired()])
    submit = SubmitField(label="Check")


mod_computadora = Blueprint('check_computadora',
                            __name__,
                            url_prefix='/computadora')


class CheckComputadora():
    """
    Clase que encapsula el manejo de posesion de Computadoras.
    :param id_computadora: id de la computadora donde se quiere registrar
                           el evento
    :type id_computadora: int
    :param key: Llave para verificar si el acceso a la computadora es válido
    :type key: string
    """
    def __init__(self, id_computadora, key):
        self.id_computadora = int(id_computadora)
        self.key = str(key)
        self.usuario = None
        self.computadora = None
        self.lugar = None
        self.lugar_activo = None
        self.reg_comp_act = None
        self.registro_toma = None

        self.obten_computadora()

    def set_usuario(self, usuario):
        """
        Configura un usuario para después ser usado por otros métodos
        :param usuario:
        :type usuario: app.models.Usuario
        """
        self.usuario = usuario

    def obten_computadora(self):
        """
        Si existe una Computadora con ese id y esa llave, entonces guarda en
        self.computadora el objeto Computadora y lo retorna. Además, en caso de
        encontrar la Computadora, guardará en self.lugar el lugar al que
        pertenece esa Computadora
        Si no existe el lugar entonces guardará y retornará None.
        :return: app.models.Computadora
        """
        query = db_sql.session.query(Computadora).filter(
            (Computadora.id == self.id_computadora) &
            (Computadora.key == str(self.key))
        )
        if query.count() > 0:
            self.computadora = query.first()
            queryLugar = db_sql.session.query(Lugar).filter(
                (Lugar.id == self.computadora.id_lugar)
            )
            self.lugar = queryLugar.first()
        else:
            self.computadora = None
            self.lugar = None
        return self.computadora

    def computadora_valida(self):
        """
        Retorna si ya está seteado una computadora válida en el objeto self
        o no.
        :return: bool
        """
        return self.computadora is not None

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
                raise ValueError("self.usuario no ha sido definido, primero \
                                  llama a self.set_usuario")
            else:
                lugar_activo = db_sql.session.query(Registro).filter(
                    (Registro.id_usuario == self.usuario.id) &
                    (Registro.fecha_hora_salida.is_(None))
                )
                if(lugar_activo.count() > 0):
                    self.lugar_activo = lugar_activo.first()
                else:
                    self.lugar_activo = None
                return self.lugar_activo
        else:
            return self.lugar_activo

    def obten_computadora_activa(self):
        """
        Obtiene la computadora que está usando el usuario guardado en
        self.usuario
        En caso de que no tenga una computadora activa retornará None.
        En caso de que no exista un usuario en self.usuario arrojará una
        excepción
        En caso de que no exista un lugar en self.lugar_activo arrojará una
        excepción
        :return: app.models.Detalle_registro
        :raises: ValueError
        """
        if self.reg_comp_act is None:
            if self.usuario is None:
                raise ValueError("self.usuario no ha sido definido, primero \
                                  llama a self.set_usuario")
            else:
                if self.lugar_activo is None:
                    raise ValueError("self.lugar_activo no ha sido definido, \
                                      primero llama a self.obten_lugar_activo")
                c_activa = db_sql.session.query(Detalle_registro).filter(
                    (Detalle_registro.fecha_hora_toma.isnot(None)) &
                    (Detalle_registro.fecha_hora_entrega.is_(None))
                ).join(Registro.detalles_registro).filter(
                    (Registro.id_usuario == self.usuario.id) &
                    (Registro.id_lugar == self.lugar_activo.id_lugar)
                )
                print(c_activa)
                print(self.usuario.id)
                print(self.lugar_activo.id_lugar)
                print(c_activa.count())
                if(c_activa.count() > 0):
                    self.reg_comp_act = c_activa.first()
                else:
                    self.reg_comp_act = None
                return self.reg_comp_act
        else:
            return self.reg_comp_act

    def is_otra_computadora_activa(self):
        """
        Retorna si el usuario guardado en self.usuario tiene una computadora
        activa distinta a la que computadora sobre la cuál se quiere aplicar un
        evento
        En caso de que no exista un usuario en self.usuario arrojará una
        excepción
        :return: bool
        :raises: ValueError
        """
        if self.usuario is None:
            raise ValueError("self.usuario no ha sido definido, primero llama \
                              a self.set_usuario")
        else:
            if self.obten_computadora_activa() is None:
                return False
            else:
                return self.reg_comp_act.id_computadora != self.computadora.id

    def registra_toma(self):
        """
        Registra el uso de una Computadora por parte del usuario guardado en
        self.usuario
        En caso de que no exista un lugar guardado en self.lugar_activo
        arrojará una excepción.
        :raises: ValueError
        """
        if self.lugar_activo is None:
            raise ValueError("self.lugar_activo no ha sido definido, primero \
                              llama a self.obten_lugar_activo")
        else:
            toma = Detalle_registro(
                            id_computadora=self.computadora.id,
                            id_registro_entrada=self.lugar_activo.id,
                            id_registro_salida=self.lugar_activo.id)
            db_sql.session.add(toma)
            db_sql.session.commit()
            self.registro_toma = toma

    def registra_deja(self):
        """
        Registra la entrega de una Computadora por parte del usuario guardado
        en self.usuario
        En caso de que no exista una computadora guardada en self.reg_comp_act
        arrojará una excepción.
        :raises: ValueError
        """
        if self.reg_comp_act is None:
            raise ValueError("self.reg_comp_act no ha sido definido, primero \
                              llama a self.obten_computadora_activa")
        else:
            self.reg_comp_act.fecha_hora_entrega = datetime.utcnow()
            db_sql.session.commit()

    def computadora_ocupada(self):
        """
        Retorna si la computadora que se intenta tomar ya está tomada por algún
        otro usuario
        :return: bool
        """
        c_ocupada = db_sql.session.query(Detalle_registro).filter(
            (Detalle_registro.id_computadora == self.computadora.id) &
            (Detalle_registro.fecha_hora_toma.isnot(None)) &
            (Detalle_registro.fecha_hora_entrega.is_(None))
        ).join(Registro.detalles_registro).filter(
            (Registro.id_usuario != self.usuario.id)
        )
        return c_ocupada.count() > 0

    def valida_toma_deja_computadora(self):
        """
        Valida que se pueda crear una adquisición de la computadora para el
        usuario guardado en self.usuario del lugar guardado en
        self.lugar_activo
        :return: bool, {:text: string, :category: string}
        """
        self.obten_lugar_activo()
        if(self.lugar_activo is None):
            return False, {'text': u'Necesitas estar dentro del lugar al que \
                           pertenece la computadora',
                           'category': 'warning'}
        else:
            self.obten_computadora_activa()
            if(self.reg_comp_act is None):
                if(self.computadora_ocupada()):
                    return False, {'text': u'La computadora está ocupada por \
                                   otro usuario',
                                   'category': 'warning'}
                else:
                    self.registra_toma()
                    return True, {'text': u'Usuario con código: ' +
                                  self.usuario.codigo + u' tomó la máquina ' +
                                  self.computadora.nombre + '@' +
                                  self.lugar.nombre,
                                  'category': 'success'}
            else:
                if(self.reg_comp_act.id_computadora == self.computadora.id):
                    self.registra_deja()
                    return True, {'text': u'Usuario con código: ' +
                                  self.usuario.codigo + u' dejó la máquina ' +
                                  self.computadora.nombre + '@' +
                                  self.lugar.nombre,
                                  'category': 'success'}
                else:
                    return False, {'text': u'No puedes tener dos \
                                   computadoras activas',
                                   'category': 'warning'}

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
            toma_deja_valido, res = self.valida_toma_deja_computadora()
        return res


@mod_computadora.route('/enlace_computadora', methods=['GET', 'POST'])
def enlace_computadora():
    key = request.args.get('key')
    id_computadora = request.args.get('id')
    check_comp = CheckComputadora(id_computadora, key)
    if check_comp.computadora_valida():
        formulario = check_comp_form(csrf_enabled=False)

        if current_user.is_authenticated:
            if 'admin' in current_user.roles:
                flash(Markup(u'Te encuentras como Admin, favor de copiar la \
                             url, <a href="' + url_for_security('logout') +
                             u'">cerrar sesión</a> y volver a usar la URL'),
                      category='danger')
                return render_template('computadora/enlace_computadora.html',
                                       id=id_computadora,
                                       key=key,
                                       nombre=check_comp.computadora.nombre,
                                       nombre_lugar=check_comp.lugar.nombre,
                                       form=formulario)
            else:
                check_comp.set_usuario(current_user)
                e, res = check_comp.valida_toma_deja_computadora()
                if(e):
                    session['l_rec'] = get_recursos_activos(current_user.id)
                flash(res['text'], category=res['category'])
                return redirect('/')
        else:
            if formulario.validate_on_submit():
                message = check_comp.valida_formulario(formulario)
                flash(message['text'], category=message['category'])

            # TODO Crear este template (quizás se haga un template 'padre'
            # para las vistas similares a esta)
            return render_template('computadora/enlace_computadora.html',
                                   id=id_computadora,
                                   key=key,
                                   nombre=check_comp.computadora.nombre,
                                   nombre_lugar=check_comp.lugar.nombre,
                                   form=formulario)
    else:
        flash(u'Error de acceso: '+str(id_computadora))
    return redirect('/')


@mod_computadora.route('/actualizar_llave_computadora/<id>')
def actualizar_llave_computadora(id):
    # TODO: Verificar si el usuario tiene permisos sobre este lugar
    if current_user.has_role('admin'):
        db_sql.session.query(Computadora.id).filter(
            (Computadora.id == id)
        ).update(
            {'key': key_utils.generate_key()}
        )
        db_sql.session.commit()
        flash(u'Se actualizó la computadora con id: '+str(id))
        return redirect(
            url_for('computadora.index_view') + '?' + '&'.join(request.args)
        )
    else:
        flash(u'No tienes los permisos necesarios para realizar esa acción')
        # FIXME: no es index, se tiene que crear una vista general
        return redirect('/')
