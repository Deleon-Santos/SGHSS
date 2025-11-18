from ..extensions import db


class Filial(db.Model): 
    __tablename__ = 'filiais'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    secretarios = db.relationship('Secretario', back_populates='filial')

    def __repr__(self):
        return f'<Filial {self.nome}>'