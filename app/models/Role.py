from flask_security import RoleMixin
from app import config

db = config.db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)
