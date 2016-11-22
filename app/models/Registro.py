from app.app import db_sql


class Registro(db_sql.Model):
    id = db_sql.Column(db_sql.Integer, primary_key=True)
    user = db_sql.Column(db_sql.Integer, unique=False)

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return '<Registro %r | %r>' % self.id, self.user
