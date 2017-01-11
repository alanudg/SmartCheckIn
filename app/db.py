# -*- coding: utf-8 -*-
from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from config import db_sql
from config import app
from models.Usuario import Usuario
from models.Rol import Rol
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db_sql, Usuario, Rol)
security = Security(app, user_datastore)
