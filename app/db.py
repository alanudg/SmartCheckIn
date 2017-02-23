# -*- coding: utf-8 -*-
from flask_security import Security
from flask_security import SQLAlchemyUserDatastore, MongoEngineUserDatastore
from config import db_sql  # , db_mongo
from config import app
from models.Usuario import Usuario
from models.Rol import Rol
# from models.User import User
# from models.Role import Role

# user_datastore = MongoEngineUserDatastore(db_mongo, User, Role)
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db_sql, Usuario, Rol)
security = Security(app, user_datastore)
