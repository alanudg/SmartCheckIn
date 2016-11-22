from flask_security import Security
# from flask_security import MongoEngineUserDatastore
from flask_security import SQLAlchemyUserDatastore
# from config import db
from config import db_sql
from config import app
# from models.User import User
# from models.Role import Role
from models.Usuario import Usuario
from models.Rol import Rol
# Setup Flask-Security
# user_datastore = MongoEngineUserDatastore(db, User, Role)
# security = Security(app, user_datastore)
user_datastore = SQLAlchemyUserDatastore(db_sql, Usuario, Rol)
security = Security(app, user_datastore)
