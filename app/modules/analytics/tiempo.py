from wtforms import DateField, validators
from flask_wtf import FlaskForm
from flask import request, flash, render_template, url_for, redirect, Markup
from flask_login import current_user


class intervalo_tiempo_form(FlaskForm):
    fecha_entrada = DateField('Start Date', format='%m/%d/%Y', validators=(
        validators.Optional(),))


def entradas():
    fecha = request.args.get('fecha_hora_entrada')
    formulario = intervalo_tiempo_form(csrf_enabled=False)
    if(current_user.is_authenticated):
        if 'admin' in current_user.roles:
            return render_template('')
