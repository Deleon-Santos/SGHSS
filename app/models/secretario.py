from ..extensions import db


class Secretario(db.Model):
    __tablename__ = 'secretarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    matricula = db.Column(db.String(50), unique=True)


    def __repr__(self):
        return f'<Secretario {self.nome}>'