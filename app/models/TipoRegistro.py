from app.config import db_sql as db


class TipoRegistro(db.Model):
    __tablename__ = 'tipo_registro'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(25), unique=True)
    registro_id = db.relationship('Registro',
                                  backref='TipoRegistro',
                                  lazy=True)

    def __unicode__(self):
        return self.nombre

    def __hash__(self):
        return hash(self.id)
