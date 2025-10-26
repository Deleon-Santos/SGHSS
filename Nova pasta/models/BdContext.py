from app import db # Iremos inicializar 'db' em app.py

class Pessoa(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(15))
    endereco = db.Column(db.String(200))

class Paciente(Pessoa):
    __tablename__ = 'pacientes'
    data_nascimento = db.Column(db.Date)
    convenio = db.Column(db.String(50))
    
    # Relacionamento 1:N com Consulta
    consultas = db.relationship('Consulta', backref='paciente', lazy=True)

class Secretario(Pessoa):
    __tablename__ = 'secretarios'
    cargo = db.Column(db.String(50))
    
    # Relacionamento N:1 (Agendamento) com Consulta
    consultas_agendadas = db.relationship('Consulta', backref='secretario', lazy=True)

class Medico(Pessoa):
    __tablename__ = 'medicos'
    crm = db.Column(db.String(20), unique=True, nullable=False)
    especialidade = db.Column(db.String(50), nullable=False)
    
    # Relacionamentos com Consulta, Medicamento e Exame
    consultas = db.relationship('Consulta', backref='medico', lazy=True)
    prescricoes = db.relationship('Medicamento', backref='medico', lazy=True)
    solicitacoes = db.relationship('Exame', backref='medico', lazy=True)

class Consulta(db.Model):
    __tablename__ = 'consultas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Agendada', nullable=False) # Agendada, Cancelada, Realizada
    diagnostico = db.Column(db.Text)
    
    # Chaves Estrangeiras (Relacionamentos)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    secretario_id = db.Column(db.Integer, db.ForeignKey('secretarios.id')) # Pode ser null se for agendamento próprio
    
    # Relacionamento 1:N com Exame e Medicamento
    exames = db.relationship('Exame', backref='consulta', lazy=True)
    medicamentos = db.relationship('Medicamento', backref='consulta', lazy=True)

class Medicamento(db.Model):
    __tablename__ = 'medicamentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    dosagem = db.Column(db.String(50))
    orientacoes = db.Column(db.Text)
    
    # Chaves Estrangeiras
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)

class Exame(db.Model):
    __tablename__ = 'exames'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    data_solicitacao = db.Column(db.Date)
    resultado = db.Column(db.Text)
    
    # Chaves Estrangeiras
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)