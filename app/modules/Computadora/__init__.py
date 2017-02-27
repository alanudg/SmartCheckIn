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


class check_computadora_form(FlaskForm):
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

    def obten_computadora_activa(self):
        """
        Obtiene la computadora que está usando el usuario guardado en
        self.usuario
        En caso de que no tenga una computadora activa retornará None.
        En caso de que no exista un usuario en self.usuario arrojará una
        excepción
        :return: app.models.Registro
        :raises: ValueError
        """
        if self.reg_comp_act is None:
            if self.usuario is None:
                raise ValueError("self.usuario no ha sido definido, primero \
                                  llama a self.set_usuario")
            else:
                if self.lugar_activo is None:
                    raise ValueError("self.usuario no ha sido definido, \
                                      primero llama a self.obten_lugar_activo")
                if self.lugar_activo.fecha_hora_entrega is None:
                    self.reg_comp_act = self.lugar_activo
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
        # FIXME
        toma = Registro(id_usuario=self.usuario.id,
                        id_lugar=self.lugar.id,
                        id_computadora=self.computadora.id,
                        tipo_registro_id=config.ID_TOMA_COMPUTADORA,
                        activo=True)
        db_sql.session.add(toma)
        db_sql.session.commit()

    def registra_deja(self):
        self.reg_comp_act.activo = False
        deja = Registro(id_usuario=self.usuario.id,
                        id_lugar=self.lugar.id,
                        id_computadora=self.computadora.id,
                        tipo_registro_id=config.ID_DEJA_COMPUTADORA,
                        activo=False)
        db_sql.session.add(deja)
        db_sql.session.commit()

    def computadora_ocupada(self):
        c_ocupada = db_sql.session.query(Registro).filter(
            (Registro.id_usuario != self.usuario.id) &
            (Registro.id_computadora == self.computadora.id) &
            (Registro.activo) &
            (Registro.tipo_registro_id == config.ID_TOMA_COMPUTADORA)
        )
        return c_ocupada.count() > 0

    def valida_toma_deja_computadora(self):
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
    check_computadora = CheckComputadora(id_computadora, key)
    if check_computadora.computadora_valida():
        formulario = check_computadora_form(csrf_enabled=False)

        if current_user.is_authenticated:
            check_computadora.set_usuario(current_user)
            e, res = check_computadora.valida_toma_deja_computadora()
            flash(res['text'], category=res['category'])
            return redirect('/')
        else:
            if formulario.validate_on_submit():
                message = check_computadora.valida_formulario(formulario)
                flash(message['text'], category=message['category'])

            # TODO Crear este template (quizás se haga un template 'padre'
            # para las vistas similares a esta)
            return render_template('enlace_computadora.html',
                                   id=id_computadora,
                                   key=key,
                                   nombre=check_computadora.computadora.nombre,
                                   nombre_lugar=check_computadora.lugar.nombre,
                                   form=formulario)
    else:
        flash(u'Error de acceso: '+str(id_computadora))
    return render_template('index.html')


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
