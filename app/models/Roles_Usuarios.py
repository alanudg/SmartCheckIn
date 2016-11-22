from app.db import db_sql as db


roles_usuarios = db.Table('roles_usuarios',
                          db.Column('user_id',
                                    db.Integer(),
                                    db.ForeignKey('usuario.id')),
                          db.Column('role_id',
                                    db.Integer(),
                                    db.ForeignKey('rol.id')))
