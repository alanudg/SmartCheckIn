from app.config import db_sql as db


class Ocupacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True)
    descripcion = db.Column(db.String(127))
    usuarios = db.relationship('Usuario',
                               backref='ocupacion',
                               lazy=True)

    def __unicode__(self):
        return self.nombre

    def __hash__(self):
        return hash(self.nombre)
