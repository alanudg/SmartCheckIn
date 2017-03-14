from wtforms import DateField, validators
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_login import current_user


class intervalo_tiempo_form(FlaskForm):
    fecha_entrada = DateField('Start Date', format='%m/%d/%Y', validators=(
        validators.Optional(),))
