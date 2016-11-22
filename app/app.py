# from flask import Flask
from flask import render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Required, Length, EqualTo, DataRequired
# from flask_mongoengine import MongoEngine
from flask_security import current_user, login_user
from flask_security.core import UserMixin, AnonymousUser
import config
from db import user_datastore
# from models.User import User
# from models.Role import Role
from models.Usuario import Usuario

app = config.app
db_sql = config.db_sql


# Create a user to test with
@app.before_first_request
def create_user():
    db_sql.drop_all()
    db_sql.create_all()
    user_datastore.create_user(email='alan', password='password')
    user_datastore.commit()
    # if(User.objects.filter(email='matt@nobien.net').count() == 0):
    #     db.security.datastore.create_user(email='matt@nobien.net',
    #                                       password='password')


class LoginForm2(FlaskForm):
    email = StringField('Correo', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Recordar', validators=[Required()])
    submit = SubmitField('Login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated():
        # if user is logged in we get out of here
        return redirect(url_for('index'))
    form = LoginForm2()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.email.data).first()
        if user is None or not user.verify_password(form.password.data) or \
                not user.verify_totp(form.token.data):
            flash('Invalid username, password or token.')
            return redirect(url_for('login'))

        # log user in
        login_user(user)
        flash('You are now logged in!')
        return redirect(url_for('index'))
    print form
    print "Form"
    return render_template('login_user.html', form2=form)


class user_role_form(FlaskForm):
    user = StringField(u'Usuario', validators=[DataRequired])
    role = StringField(u'Rol', validators=[DataRequired])
    submit = SubmitField(label="Ligar")


@app.route('/user_role/<user>/<role>')
def user_role(user, role):
    form = user_role_form()
    return render_template('user_role.html', form=form, user=user, role=role)


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
