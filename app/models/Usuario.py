from flask_security import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import db_sql as db
from app.models.Roles_Usuarios import roles_usuarios


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    active = db.Column(db.Boolean())
    last_login_at = db.Column(db.String(255))
    current_login_at = db.Column(db.String(255))
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Rol',
                            secondary=roles_usuarios,
                            backref=db.backref('users',
                                               lazy='dynamic'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
