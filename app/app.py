# -*- coding: utf-8 -*-
from flask import render_template, flash
from flask_wtf import FlaskForm
from flask_qrcode import QRcode
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, DataRequired
# from flask_mongoengine import MongoEngine
from flask_security.core import UserMixin, AnonymousUser
import config
from db import user_datastore
from utils import db_utils, admin_utils
from flask_admin import Admin
from modules import mod_lugar, mod_computadora

app = config.app
db_sql = config.db_sql


# Create a user to test with
@app.before_first_request
def create_db():
    db_utils.create_sample_db(db_sql, user_datastore)


# Initialize Flask-Admin
admin = Admin(app,
              template_mode='bootstrap3',
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

@app.route('/analytics')
# @login_required
def analytics():
    user = UserMixin
    if user.is_anonymous:
        user = AnonymousUser
    return render_template('analytics.html', user=user)


app.register_blueprint(mod_lugar)
app.register_blueprint(mod_computadora)

if __name__ == '__main__':
    app.run()
