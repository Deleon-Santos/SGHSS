from datetime import datetime, date, time
from app.models.consulta import Consulta
from app.models.filial import Filial
from app.models.paciente import Paciente
from app.models.secretario import Secretario
from ..extensions import db
from app.models.medico import Medico
from werkzeug.security import generate_password_hash

# 
def seed_db(app):
    with app.app_context():
        
        db.create_all()
        if Medico.query.first():
            return
        try:
        # Criação da filial
            filial1 = Filial(nome='Filial Central', endereco='Rua Principal, 123', telefone='1234-5678')
            db.session.add(filial1)

        # Criação do secretário
            sec1 = Secretario(nome='Deleon Santos', matricula='4556949', usuario= 'deleon@santos', senha=generate_password_hash('4556949'), nivel_acesso='secretario',filial_id=1)
            db.session.add(sec1)
            
            # Criação dos médicos
            plant = Medico(nome='Plantonista', crm='CRM000', especialidade='Plantonista', usuario='plantonista@plantonista', senha=generate_password_hash('crm000'), nivel_acesso='medico')
            med1 = Medico(nome='Dr. João Alcantara', crm='CRM123', especialidade='Clinico_geral', usuario='joao@alcantara', senha=generate_password_hash('crm123'), nivel_acesso='medico')
            med2 = Medico(nome='Dr. Maria Magalhaes', crm='CRM456', especialidade='Pediatria', usuario='maria@magalhaes', senha=generate_password_hash('crm456'), nivel_acesso='medico')
            med3 = Medico(nome='Dr. Pedro Cardoso', crm='CRM789', especialidade='Obstetricia', usuario='pedro@cardoso', senha=generate_password_hash('crm789'), nivel_acesso='medico')
            db.session.add_all([med1, med2, med3, plant])

            # Criação dos pacientes
            pac1 = Paciente(nome='Alice Souza', data_nascimento=date(2000, 12, 12), cpf='12345678901', usuario='alice@souza', senha=generate_password_hash('12345678901'), nivel_acesso='paciente')
            pac2 = Paciente(nome='Bruno Santos', data_nascimento=date(2000, 8, 12), cpf='23456789012', usuario='bruno@santos', senha=generate_password_hash('23456789012'), nivel_acesso='paciente')
            pac3 = Paciente(nome='Carla Castro' , data_nascimento=date(2000, 10, 12), cpf='34567890123', usuario='carla@caastro', senha=generate_password_hash('34567890123'), nivel_acesso='paciente')
            db.session.add_all([pac1, pac2, pac3])

            db.session.commit()  # Precisa para pegar IDs

            # Criação das consultas (1 paciente por médico)
            cons1 = Consulta(medico_id=med1.id, paciente_id=pac1.id, data=datetime.now().date(), hora=time(9, 0), secretario_id=sec1.id,status='Agendada')
            cons2 = Consulta(medico_id=med2.id, paciente_id=pac2.id, data=datetime.now().date(), hora=time(10, 0),secretario_id=sec1.id,status='Agendada')
            cons3 = Consulta(medico_id=med3.id, paciente_id=pac3.id, data=datetime.now().date(), hora=time(11, 0),secretario_id=sec1.id, status='Agendada')

            db.session.add_all([cons1, cons2, cons3])

            db.session.commit()
            print("Banco inicializado com médicos, pacientes e consultas!")
            return
        except Exception as e:
            db.session.rollback()
            print("Erro ao executar seed:", str(e))
            raise
        