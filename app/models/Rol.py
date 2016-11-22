from flask_security import RoleMixin
from app.config import db_sql


class Rol(db_sql.Model, RoleMixin):
    id = db_sql.Column(db_sql.Integer(), primary_key=True)
    name = db_sql.Column(db_sql.String(80), unique=True)
    description = db_sql.Column(db_sql.String(255))
