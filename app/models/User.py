from flask_security import UserMixin
from app import config
from app.models.Role import Role

db = config.db


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    last_login_at = db.StringField(max_length=255)
    current_login_at = db.StringField(max_length=255)
    last_login_ip = db.StringField(max_length=255)
    current_login_ip = db.StringField(max_length=255)
    login_count = db.StringField(max_length=255)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
