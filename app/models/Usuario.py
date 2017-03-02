from flask_security import UserMixin
from app.config import db_sql as db
from app.models.Roles_Usuarios import roles_usuarios
from app.models.Lugares_Usuarios import lugares_usuarios


class Usuario(db.Model, UserMixin):
    # Datos indizados
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    # Datos de login
    password = db.Column(db.String(512))
    # Datos extra
    codigo = db.Column(db.String(15), unique=True)
    nip = db.Column(db.String(4))
    apellido_paterno = db.Column(db.String(20))
    apellido_materno = db.Column(db.String(20))
    nombres = db.Column(db.String(30))
    # Datos de seguridad
    active = db.Column(db.Boolean())
    last_login_at = db.Column(db.String(255))
    current_login_at = db.Column(db.String(255))
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime())
    # Relaciones
    id_ocupacion = db.Column(db.Integer, db.ForeignKey('ocupacion.id'))
    registros = db.relationship('Registro', backref='Usuario', lazy=True)
    roles = db.relationship('Rol',
                            secondary=roles_usuarios,
                            backref=db.backref('usuarios',
                                               lazy='dynamic'))
    lugares = db.relationship('Lugar',
                              secondary=lugares_usuarios,
                              backref=db.backref('usuarios',
                                                 lazy='dynamic'))

    def __unicode__(self):
        return self.email

    def __hash__(self):
        return hash(self.email)
    # @property
    # def password(self):
    #     # raise AttributeError('password is not a readable attribute')
    #     return self.password_hash
    #
    # @password.setter
    # def password(self, password):
    #     self.password_hash = generate_password_hash(password)
    #
    # def verify_password(self, password):
    #     return check_password_hash(self.password_hash, password)
