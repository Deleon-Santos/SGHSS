from ..extensions import db


class Medicamento(db.Model):
    __tablename__ = 'medicamentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    dosagem = db.Column(db.String(120))
    orientacoes = db.Column(db.Text)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)


    consulta = db.relationship('Consulta', back_populates='medicamentos')


    def __repr__(self):
        return f'<Medicamento {self.nome}>'