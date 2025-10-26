from ..extensions import db
from datetime import date


class Exame(db.Model):
    __tablename__ = 'exames'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(200), nullable=False)
    data_solicitacao = db.Column(db.Date, default=date.today)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)


    consulta = db.relationship('Consulta', back_populates='exames')


    def __repr__(self):
        return f'<Exame {self.tipo}>'