# -*- coding: utf-8 -*-
from flask import render_template, flash, Markup, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import Required, Length, DataRequired
# from flask_mongoengine import MongoEngine
from flask_security import utils, current_user
from flask_security.core import UserMixin, AnonymousUser
import config
import random
from db import user_datastore
from utils import db_utils
from models.Usuario import Usuario
from models.Rol import Rol
from models.Ocupacion import Ocupacion
from models.Lugar import Lugar
from models.Computadora import Computadora
from models.Registro import Registro
from flask_admin.contrib import sqla
from flask_admin.contrib import geoa
from flask_admin import Admin

app = config.app
db_sql = config.db_sql


# Create a user to test with
@app.before_first_request
def create_db():
    db_utils.create_sample_db(db_sql, user_datastore)


class momentjs(object):
    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-dates-and-times
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        # return Markup("<span data-date=\"%s\" data-format=\"%s\"></span>"
        #               % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"),
        #                  format))
        return Markup("<span data-date=\"%s\" data-format=\"%s\"></span>"
                      % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")


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
    with app.test_request_context():
        momentEsRoute = 'bower_components/moment/locale/es.js'
        momentRoute = 'bower_components/moment/min/moment.min.js'
        extra_js = [url_for('static', filename=momentRoute),
                    url_for('static', filename=momentEsRoute)]
    # FIXME: se tiene que obtener el formato (en este caso fromNow) de
    # data-format
    extra_js_code = [Markup('moment.locale(\'es\');\
$("[data-date]").each(function(k, el){\
    var $el = $(el);\
    var momentTime = moment(new Date($el.attr(\'data-date\')));\
    $el.html(momentTime.fromNow());\
    $el.attr(\'title\', momentTime.format(\'dddd, MMMM Do YYYY, h:mm:ss a\'));\
    $el.attr(\'alt\', momentTime.format(\'dddd, MMMM Do YYYY, h:mm:ss a\'));\
})')]
    # can_create = False
    can_edit = False
    can_delete = False

    with app.test_request_context():
        column_formatters = {'fecha_hora': lambda v, c, m,
                             p: momentjs(m.fecha_hora).calendar(),
                             'Usuario.codigo': lambda v, c, m, p: Markup(
                                    "<a href='%s'>%s</a>" % (
                                        url_for('registro.index_view',
                                                flt0_9=m.Usuario.email),
                                        m.Usuario.codigo))
                             }

    column_filters = ['fecha_hora', 'Usuario.email', 'Usuario.codigo']

    def is_accessible(self):
        return current_user.has_role('admin')


# Initialize Flask-Admin
admin = Admin(app,
              template_mode='bootstrap3',
              base_template='/admin/my_index.html',
              url='/admin')

admin.add_view(UserAdmin(Usuario, db_sql.session))
admin.add_view(RoleAdmin(Rol, db_sql.session))
admin.add_view(OcupacionAdmin(Ocupacion, db_sql.session))
admin.add_view(LugarAdmin(Lugar, db_sql.session))
admin.add_view(ComputadoraAdmin(Computadora, db_sql.session))
admin.add_view(RegistroAdmin(Registro, db_sql.session))


class user_role_form(FlaskForm):
    user = StringField(u'Usuario', validators=[DataRequired])
    role = StringField(u'Rol', validators=[DataRequired])
    submit = SubmitField(label="Ligar")


@app.route('/user_role/<user>/<role>', methods=['GET', 'POST'])
def user_role(user, role):
    form = user_role_form()
    return render_template('user_role.html', form=form, user=user, role=role)


class LugarForm(FlaskForm):
    nombre = StringField('Nombre', validators=[Required(), Length(1, 64)])
    puntos = TextAreaField()

    submit = SubmitField('Crear')


@app.route('/maps', methods=['GET', 'POST'])
def maps():
    form = LugarForm()
    if form.validate_on_submit():
        flash('Mapa creado!')
        return render_template('maps.html', form=form, validado='True')
    return render_template('maps.html', form=form, validado='False')

# app.add_url_rule('/user_role/<user>/<role>', view_func=user_role)


# Views
@app.route('/')
# @login_required
def home():
    user = UserMixin
    if user.is_anonymous:
        user = AnonymousUser
    return render_template('index.html', user=user)


if __name__ == '__main__':
    app.run()
