# -*- coding: utf-8 -*-
from flask_admin.contrib import sqla, geoa
from app.utils.render_utils import momentjs, render_list_link, render_qr
from flask_login import current_user
from flask import Markup, url_for
from wtforms import PasswordField
from app.models.Usuario import Usuario
from app.models.Rol import Rol
from app.models.Ocupacion import Ocupacion
from app.models.Lugar import Lugar
from app.models.Computadora import Computadora
from app.models.Registro import Registro

class UserAdmin(sqla.ModelView):

    column_exclude_list = list = ('password', )

    form_excluded_columns = ('password', 'nip', 'registro_id', 'last_login_at',
                             'current_login_at', 'last_login_ip',
                             'current_login_at', 'login_count', 'confirmed_at',
                             'current_login_ip')

    # Automatically display human-readable names for the current and available
    # Roles when creating or editing a User
    column_auto_select_related = True

    column_searchable_list = (Usuario.email,)

    form_args = dict(
        roles=dict(
            default=(None, 'end-user'),
        ),
        ocupacion=dict(
            label=u'Ocupación',
        ),
    )

    def is_accessible(self):
        return current_user.has_role('admin')

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()

        form_class.password2 = PasswordField('Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = utils.encrypt_password(model.password2)
        if(is_created):
            model.nip = random.randint(1111, 9999)
            # https://realpython.com/blog/python/handling-email-confirmation-in-flask/

        flash(Markup(u"Se envió un correo a: <b>" + str(model.email) + "</b>" +
                     u"<br>Código: <b>" + str(model.codigo) + "</b>" +
                     u"<br>Nip: <b>" + str(model.nip) + "</b>"))


class RoleAdmin(sqla.ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')


class OcupacionAdmin(sqla.ModelView):
    form_excluded_columns = list = ('usuarios',)

    def is_accessible(self):
        return current_user.has_role('admin')


class LugarAdmin(geoa.ModelView):

    list_template = 'admin/Lugar/list.html'
    create_template = 'admin/Lugar/create.html'
    edit_template = 'admin/Lugar/edit.html'
    form_excluded_columns = list = ('computadora_id', 'registro_id', )
    column_list = ('nombre', 'coordenadas', 'hora_apertura', 'hora_cierre',
                    'QR', 'key')
    column_formatters = {
        'QR': (lambda v, c, m, p:
                    render_qr(v, c, m, p,
                              [('id', m.id), ('key', m.key)],
                              'enlace_lugar')),
        'key': (lambda v, c, m, p:
                Markup("%s <a href='%s'>\
                            <span class='glyphicon glyphicon-refresh'></span>\
                        </a>" % (m.key, url_for('actualizar_llave_lugar', id=m.id)))
                )
    }
    def is_accessible(self):
        return current_user.has_role('admin')


class ComputadoraAdmin(sqla.ModelView):
    form_excluded_columns = list = ('registro_id', )

    def is_accessible(self):
        return current_user.has_role('admin')


class RegistroAdmin(sqla.ModelView):
    form_excluded_columns = list = ('fecha_hora', )
    column_list = list = ('fecha_hora', 'Lugar', 'Usuario',
                          'Usuario.codigo', 'Computadora', 'TipoRegistro')
    can_create = False
    can_edit = False
    can_delete = False

    # with app.test_request_context():
    column_formatters = {
        'fecha_hora': lambda v, c, m, p: momentjs(m.fecha_hora).fromNow(),
        'Usuario.codigo': (lambda v, c, m, p:
                           render_list_link(v, c, m, p,
                                       'flt2_23',
                                       m.Usuario.codigo,
                                       m.Usuario.codigo)),
        'Lugar': (lambda v, c, m, p:
                  render_list_link(v, c, m, p,
                              'flt0_9',
                              m.Lugar.nombre,
                              m.Lugar.nombre)),
        'Usuario': (lambda v, c, m, p:
                    render_list_link(v, c, m, p,
                                'flt1_16',
                                m.Usuario.email,
                                m.Usuario.email)),
        'Computadora': (lambda v, c, m, p:
                        render_list_link(v, c, m, p,
                                    'flt3_30',
                                    m.Computadora.nombre,
                                    m.Computadora.nombre)
                        if m.Computadora is not None else
                        render_list_link(v, c, m, p,
                                    'flt5_32',
                                    '1',
                                    'NULL')
                        ),
        'TipoRegistro': (lambda v, c, m, p:
                         render_list_link(v, c, m, p,
                                     'flt6_37',
                                     m.TipoRegistro.nombre,
                                     m.TipoRegistro.nombre)),
         }

    column_filters = ['fecha_hora', 'Lugar.nombre', 'Usuario.email',
                      'Usuario.codigo', 'Computadora', 'TipoRegistro']

    list_template = 'admin/list_moment.html'

    def is_accessible(self):
        return current_user.has_role('admin')
