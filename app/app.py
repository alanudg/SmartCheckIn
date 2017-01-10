# from flask import Flask
from flask import render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import Required, Length, DataRequired
# from flask_mongoengine import MongoEngine
from flask_security import utils, current_user
from flask_security.core import UserMixin, AnonymousUser
import config
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


class UserAdmin(sqla.ModelView):

    column_exclude_list = list = ('password', )

    form_excluded_columns = ('password', 'registro_id', )

    # Automatically display human-readable names for the current and available
    # Roles when creating or editing a User
    column_auto_select_related = True

    column_searchable_list = (Usuario.email,)

    def is_accessible(self):
        return current_user.has_role('admin')

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()

        form_class.password2 = PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = utils.encrypt_password(model.password2)


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
    # can_create = False

    def is_accessible(self):
        return current_user.has_role('admin')


# Initialize Flask-Admin
admin = Admin(app, template_mode='bootstrap3')

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
