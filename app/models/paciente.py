from ..extensions import db


class Paciente(db.Model):
    __tablename__ = 'pacientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    data_nascimento = db.Column(db.Date)
    cpf = db.Column(db.String(20), unique=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(20), nullable=False)
    nivel_acesso = db.Column(db.String(20), nullable=False, default='paciente')

    consultas = db.relationship('Consulta', back_populates='paciente')


    def __repr__(self):
        return f'<Paciente {self.nome}>'