from ..extensions import db


class Secretario(db.Model):
    __tablename__ = 'secretarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    matricula = db.Column(db.String(50), unique=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(20), nullable=False)
    nivel_acesso = db.Column(db.String(20), nullable=False, default='secretario')

    def __repr__(self):
        return f'<Secretario {self.nome}>'