import os
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
import json
from flask_bootstrap import Bootstrap
#
# Create app
app = Flask(__name__)
Bootstrap(app)

app.config['BOOTSTRAP_SERVE_LOCAL'] = True

app.config['SECRET_KEY'] = '123456789'

app.config['PORT'] = int(os.getenv('VCAP_APP_PORT', 5000))

app.config['HOST'] = '127.0.0.1' if "VCAP_APP_HOST" in os.environ \
    else '0.0.0.0'

app.config['DEBUG'] = True if "VCAP_APP_HOST" in os.environ else True

# # MongoDB Config
if 'VCAP_SERVICES' in os.environ:
    mongodbService = json.loads(os.environ['VCAP_SERVICES'])['mongodb'][0]
    mongodbCred = mongodbService['credentials']
    # app.config['MONGO_DB_CREDENTIALS'] = mongodbCred
    app.config['MONGODB_DB'] = str(mongodbCred['name'])
    app.config['MONGODB_HOST'] = str(mongodbCred['host'])
    app.config['MONGODB_PORT'] = int(mongodbCred['port'])
    app.config['MONGODB_USERNAME'] = str(mongodbCred['username'])
    app.config['MONGODB_PASSWORD'] = str(mongodbCred['password'])
    # TODO: Load psql config from VCAP_SERVICES
else:
    app.config['MONGODB_DB'] = 'prueba'
    app.config['MONGODB_HOST'] = 'localhost'
    app.config['MONGODB_PORT'] = 27017
    conector = 'postgresql+psycopg2'
    user = 'nombre_usuario'
    password = 'tu_password'
    db_name = 'tu_base_de_datos'
    psql_uri = conector+'://'+user+':'+password+'@localhost/'+db_name
    app.config['SQLALCHEMY_DATABASE_URI'] = psql_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#
# app.config['SECURITY_TRACKABLE'] = True
#
# Create database connection object
db = MongoEngine(app)
db_sql = SQLAlchemy(app)
