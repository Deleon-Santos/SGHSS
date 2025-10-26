from ..extensions import db


class Medico(db.Model):
    __tablename__ = 'medicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    crm = db.Column(db.String(50), unique=True)
    especialidade = db.Column(db.String(80))


    consultas = db.relationship('Consulta', back_populates='medico')
    def __repr__(self):
        return f'<Medico {self.nome}>'