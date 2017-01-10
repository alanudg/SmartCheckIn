from app.config import db_sql as db


class TipoRegistro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(25), unique=True)

    def __unicode__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)
