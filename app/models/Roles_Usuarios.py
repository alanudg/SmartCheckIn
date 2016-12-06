from app.db import db_sql as db


roles_usuarios = db.Table('roles_usuarios',
                          db.Column('id_usuario',
                                    db.Integer(),
                                    db.ForeignKey('usuario.id')),
                          db.Column('id_rol',
                                    db.Integer(),
                                    db.ForeignKey('rol.id')))
