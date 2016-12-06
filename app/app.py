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
from models.Usuario import Usuario
from models.Rol import Rol
from models.Ocupacion import Ocupacion
from flask_admin.contrib import sqla
from flask_admin import Admin

app = config.app
db_sql = config.db_sql


# Create a user to test with
@app.before_first_request
def create_user():
    db_sql.drop_all()
    db_sql.create_all()

    ocupacion_alumno = Ocupacion(nombre='Alumno',
                                 descripcion='Alumno perteneciente al CUCEA')
    db_sql.session.add(ocupacion_alumno)
    db_sql.session.commit()
    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin',
                                       description='Administrator')
    user_datastore.find_or_create_role(name='end-user',
                                       description='End user')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility
    # function to encrypt the password.
    encrypted_password = utils.encrypt_password('password')
    if not user_datastore.get_user('alan'):
        user_datastore.create_user(email='alan', password=encrypted_password)
    if not user_datastore.get_user('admin'):
        user_datastore.create_user(email='admin', password=encrypted_password)

    # Commit any database changes;
    # the User and Roles must exist before we can add a Role to the User
    db_sql.session.commit()

    # Give one User has the "end-user" role, while the other
    # has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user('alan', 'end-user')
    user_datastore.add_role_to_user('admin', 'admin')
    db_sql.session.commit()

    #
    # https://gist.github.com/skyuplam/ffb1b5f12d7ad787f6e4
    #


# Customized User model for SQL-Admin
class UserAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    # Don't include the standard password field when creating or editing
    # a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available
    # Roles when creating or editing a User
    column_auto_select_related = True

    column_searchable_list = (Usuario.email,)

    # Prevent administration of Users unless the currently logged-in user
    # has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field
    # corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password
    # before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a
    # regular text field.
    def scaffold_form(self):
        # Start with the standard form as provided by Flask-Admin.
        # We've already told Flask-Admin to exclude the password field from
        # this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it
        # "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or
    # edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the
            # database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):
    # Prevent administration of Roles unless the currently logged-in user
    # has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')


class OcupacionAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    form_excluded_columns = list = ('usuarios',)

    def is_accessible(self):
        return current_user.has_role('admin')


# Initialize Flask-Admin
admin = Admin(app, template_mode='bootstrap3')

admin.add_view(UserAdmin(Usuario, db_sql.session))
admin.add_view(RoleAdmin(Rol, db_sql.session))
admin.add_view(OcupacionAdmin(Ocupacion, db_sql.session))


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
