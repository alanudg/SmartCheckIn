# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_qrcode import QRcode
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import Required, Length, DataRequired
# from flask_mongoengine import MongoEngine
from flask_security.core import UserMixin, AnonymousUser
import config
from db import user_datastore
from utils import db_utils, admin_utils, key_utils
from flask_admin import Admin
from models import Lugar

app = config.app
db_sql = config.db_sql


# Create a user to test with
@app.before_first_request
def create_db():
    db_utils.create_sample_db(db_sql, user_datastore)


# Initialize Flask-Admin
admin = Admin(app,
              template_mode='bootstrap3',
              base_template='/admin/my_index.html',
              url='/admin')

admin_utils.load_model_views(admin, db_sql)

qrcode = QRcode(app)


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


class registra_entrada_salida_lugar(FlaskForm):
    codigo = StringField(u'Código', validators=[DataRequired()])
    nip = PasswordField(u'Nip', validators=[DataRequired()])
    submit = SubmitField(label="Check")


@app.route('/enlace_lugar', methods=['GET', 'POST'])
def enlace_lugar():
    key = request.args.get('key')
    id = request.args.get('id')
    query = db_sql.session.query(Lugar.id, Lugar.nombre).filter(
        (Lugar.id == id) & (Lugar.key == str(key))
    )
    if query.count() > 0:
        lugar = query.first()
        nombre = lugar.nombre
        formulario = registra_entrada_salida_lugar()

        if current_user.is_authenticated:
            flash(u'Evento en el lugar con id: ' + str(id) + str(lugar.nombre))
        else:
            # TODO: Validar codigo y nip del usuario
            if formulario.validate_on_submit():
                print 'After submit'
            else:
                print 'Before submit'
            # TODO: En enlace_lugar, poner QR?
        return render_template('enlace_lugar.html',
                               id=id,
                               key=key,
                               nombre=nombre,
                               form=formulario)
    else:
        flash(u'Error de acceso: '+str(id))
    return render_template('index.html')


@app.route('/actualizar_llave_lugar/<id>')
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


if __name__ == '__main__':
    app.run()
