from ..extensions import db
from datetime import date, time


class Consulta(db.Model):
    __tablename__ = 'consultas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    secretario_id = db.Column(db.Integer, db.ForeignKey('secretarios.id'), nullable=True)
    status = db.Column(db.String(30), default='Agendada')
    diagnostico = db.Column(db.Text)


    paciente = db.relationship('Paciente', back_populates='consultas')
    medico = db.relationship('Medico', back_populates='consultas')


    medicamentos = db.relationship('Medicamento', back_populates='consulta', cascade='all, delete-orphan')
    exames = db.relationship('Exame', back_populates='consulta', cascade='all, delete-orphan')


    def __repr__(self):
        return f'<Consulta {self.id}- {self.data} {self.hora}>'