from flask import Flask
from datetime import datetime
from app.database.data import seed_db
from app.models.consulta import Consulta
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.routes import consultas
from .config import Config
from .extensions import db
#from flask_restx import Api



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # api = Api(app, version='1.0', title='SGHSS API',
    #           description='API para gerenciamento de médicos, pacientes e consultas')

    
    from .routes import consultas_bp
    app.register_blueprint(consultas_bp)

    
    with app.app_context():
        db.create_all() 
        print('Tabelas verificadas e criadas se necessário!')
        seed_db(app)
    
    
    
    return app
