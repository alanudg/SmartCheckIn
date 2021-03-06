# -*- coding: utf-8 -*-
from flask import render_template, flash, request, session
from flask_wtf import FlaskForm
from flask_qrcode import QRcode
from flask_apidoc import ApiDoc
from flask_security import current_user
from flask_login import user_logged_in, user_logged_out
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, DataRequired
# from flask_mongoengine import MongoEngine
from flask_security.core import UserMixin, AnonymousUser
import config
from db import user_datastore
from utils import db_utils, admin_utils
from flask_admin import Admin
from modules import mod_lugar, mod_computadora, Session, MQTT
from api import mod_api
import json
from utils import render_utils
from models import Detalle_registro, Registro, Lugar, Computadora

app = config.app
db_sql = config.db_sql

doc = ApiDoc(app=app, url_path='/api/docs', dynamic_url=False)


# Create a user to test with
@app.before_first_request
def create_db():
    db_utils.create_sample_db(db_sql, user_datastore)
    MQTT()


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
    recursos_olvidados = db_sql.session.query(Detalle_registro).filter(
        Detalle_registro.fecha_hora_entrega.is_(None)
    ).join(Registro.detalles_registro_salida).filter(
        Registro.fecha_hora_salida.isnot(None)
    ).join(Computadora, Lugar)

    return render_template('index.html',
                           user=user,
                           recursos_olvidados=recursos_olvidados.all(),
                           render_moment=render_utils.momentjs)


@user_logged_in.connect_via(app)
def set_session(sender, user):
    session['l_act'] = Session.get_lugares_activos(current_user.id)
    session['l_rec'] = Session.get_recursos_activos(current_user.id)


@user_logged_out.connect_via(app)
def erase_session(sender, user):
    session.clear()


@app.route('/analytics')
# @login_required
def analytics():
    user = UserMixin
    if user.is_anonymous:
        user = AnonymousUser
    return render_template('analytics/analytics.html', user=user)


@app.route('/genera_token', methods=['POST'])
def genera_token():
    print 'data:' + str(json.loads(request.data))
    json_data = json.loads(request.data)
    my_string = ''
    for k in json_data:
        my_string += str(k) + ' : ' + str(json_data[k]) + ', '
    return 'TAG: (' + my_string + ')'


app.register_blueprint(mod_lugar)
app.register_blueprint(mod_computadora)
app.register_blueprint(mod_api)


if __name__ == '__main__':
    app.run()
