from datetime import datetime, date, time
from app.models.consulta import Consulta
from app.models.paciente import Paciente
from app.models.secretario import Secretario
from ..extensions import db
from app.models.medico import Medico

# 
def seed_db(app):
    with app.app_context():
        
        db.create_all()
        if Medico.query.first():
            return
        
        # Criação do secretário
        sec1 = Secretario(nome='Deleon Santos', matricula='4556949', usuario= 'DeleonSantos', senha='4556949')
        db.session.add(sec1)
        
        # Criação dos médicos
        med1 = Medico(nome='Dr. João Alcantara', crm='CRM123', especialidade='clinico_geral', usuario='JoaoAlcantara', senha='CRM123')
        med2 = Medico(nome='Dr. Maria Magalhaes', crm='CRM456', especialidade='pediatria', usuario='MariaMagalhaes', senha='CRM456')
        med3 = Medico(nome='Dr. Pedro Cardoso', crm='CRM789', especialidade='obstetricia', usuario='PedroCardoso', senha='CRM789')
        db.session.add_all([med1, med2, med3])

        # Criação dos pacientes
        pac1 = Paciente(nome='Alice Souza', data_nascimento=date(2000, 12, 12), cpf='12345678901', usuario='AliceSouza', senha='12345678901')
        pac2 = Paciente(nome='Bruno Santos', data_nascimento=date(2000, 8, 12), cpf='23456789012', usuario='BrunoSantos', senha='23456789012')
        pac3 = Paciente(nome='Carla Castro' , data_nascimento=date(2000, 10, 12), cpf='34567890123', usuario='CarlaCastro', senha='34567890123')
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