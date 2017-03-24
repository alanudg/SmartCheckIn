# -*- coding: utf-8 -*-
from app.models import Ocupacion, Lugar, Computadora, Registro, \
                       Detalle_registro
from datetime import datetime, timedelta
from flask_security import utils


def create_sample_db(db_sql, user_datastore):
    """
        It removes any database that currently exists and create a new one.

        :param db_sql:
            SQLAlchemy instance
        :param user_datastore:
            SQLAlchemyUserDatastore instance
    """
    db_sql.drop_all()
    db_sql.create_all()

    ocup_alumno = Ocupacion(nombre='Alumno',
                            descripcion='Alumno perteneciente al CUCEA')
    db_sql.session.add(ocup_alumno)
    l_cucea = Lugar(nombre='CUCEA',
                    coordenadas='POLYGON((-103.383085727692 \
                                 20.7399807434582, \
                                 -103.378794193268 \
                                 20.7391780551767, \
                                 -103.377120494843 \
                                 20.7447967837201, \
                                 -103.3789229393 \
                                 20.7447967837201, \
                                 -103.379480838776 \
                                 20.7445559853482, \
                                 -103.381283283234 \
                                 20.7448770497589, \
                                 -103.383085727692 \
                                 20.7399807434582))')
    l_cici = Lugar(nombre='CICI',
                   coordenadas='POLYGON((-103.378770053387 \
                                20.7441044873678, \
                                -103.378748595715 \
                                20.7439991376452, \
                                -103.378555476665 \
                                20.7440242209191, \
                                -103.378555476665 \
                                20.7441245539733, \
                                -103.378770053387 \
                                20.7441044873678))',
                   lugar_padre=l_cucea)
    db_sql.session.add(l_cici)
    db_sql.session.commit()

    computadora1 = Computadora(nombre='dev01', id_lugar=l_cici.id)
    db_sql.session.add(computadora1)
    computadora2 = Computadora(nombre='dev02', id_lugar=l_cici.id)
    db_sql.session.add(computadora2)
    db_sql.session.commit()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin',
                                       description='Administrator')
    user_datastore.find_or_create_role(name='end-user',
                                       description='End user')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility
    # function to encrypt the password.
    encrypted_password = utils.encrypt_password('password')
    if not user_datastore.get_user('alan'):
        user_datastore.create_user(email='alan',
                                   password=encrypted_password,
                                   id_ocupacion=ocup_alumno.id,
                                   codigo='208696345',
                                   nip='1111',
                                   apellido_paterno='Sánchez',
                                   apellido_materno='Castro',
                                   nombres='Alan Andrés',
                                   lugares=[l_cici]
                                   )
    if not user_datastore.get_user('andres'):
        user_datastore.create_user(email='andres',
                                   password=encrypted_password,
                                   id_ocupacion=ocup_alumno.id,
                                   codigo='1234',
                                   nip='1111',
                                   apellido_paterno='Sánchez',
                                   apellido_materno='Castro',
                                   nombres='Alan Andrés',
                                   lugares=[l_cici]
                                   )
    if not user_datastore.get_user('admin'):
        user_datastore.create_user(email='admin',
                                   password=encrypted_password)

    # Commit any database changes;
    # the User and Roles must exist before we can add a Role to the User
    db_sql.session.commit()

    # Give one User has the "end-user" role, while the other
    # has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user('alan', 'end-user')
    user_datastore.add_role_to_user('andres', 'end-user')
    user_datastore.add_role_to_user('admin', 'admin')
    user_datastore.add_role_to_user('admin', 'end-user')
    db_sql.session.commit()

    alan = user_datastore.get_user('alan')
    andres = user_datastore.get_user('andres')

    entrada1 = Registro(id_usuario=alan.id,
                        id_lugar=l_cici.id,
                        fecha_hora_entrada=datetime.utcnow() -
                        timedelta(minutes=10))
    db_sql.session.add(entrada1)
    db_sql.session.commit()

    toma1 = Detalle_registro(
                    id_computadora=computadora1.id,
                    id_registro_entrada=entrada1.id,
                    id_registro_salida=entrada1.id,
                    fecha_hora_toma=datetime.utcnow() - timedelta(minutes=8),
                    fecha_hora_entrega=datetime.utcnow() - timedelta(minutes=6)
                    )
    db_sql.session.add(toma1)
    db_sql.session.commit()

    toma2 = Detalle_registro(
                    id_computadora=computadora2.id,
                    id_registro_entrada=entrada1.id,
                    id_registro_salida=entrada1.id,
                    fecha_hora_toma=datetime.utcnow() - timedelta(minutes=5),

                    )
    db_sql.session.add(toma2)
    db_sql.session.commit()

    entrada1.fecha_hora_salida = datetime.utcnow() - timedelta(minutes=2)
    db_sql.session.commit()

    entrada2 = Registro(id_usuario=andres.id,
                        id_lugar=l_cici.id,
                        fecha_hora_entrada=datetime.utcnow() -
                        timedelta(minutes=60))
    db_sql.session.add(entrada2)
    db_sql.session.commit()

    entrada3 = Registro(id_usuario=alan.id,
                        id_lugar=l_cici.id,
                        fecha_hora_entrada=datetime.utcnow() -
                        timedelta(minutes=70))
    db_sql.session.add(entrada3)
    db_sql.session.commit()

    toma2.id_registro_salida = entrada3.id
    toma2.fecha_hora_entrega = datetime.utcnow() - timedelta(minutes=4)

    toma3 = Detalle_registro(
                    id_computadora=computadora1.id,
                    id_registro_entrada=entrada3.id,
                    id_registro_salida=entrada3.id,
                    fecha_hora_toma=datetime.utcnow() - timedelta(minutes=65),
                    )
    db_sql.session.add(toma3)
    db_sql.session.commit()

    entrada3.fecha_hora_salida = datetime.utcnow() - timedelta(minutes=60)
    db_sql.session.commit()
