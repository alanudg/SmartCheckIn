from app.db import db_sql as db


lugares_usuarios = db.Table('lugares_usuarios',
                            db.Column('id_usuario',
                                      db.Integer(),
                                      db.ForeignKey('usuario.id')),
                            db.Column('id_lugar',
                                      db.Integer(),
                                      db.ForeignKey('lugar.id')))
