from flask import Flask, redirect, url_for
from flask_swagger_ui import get_swaggerui_blueprint
from app.database.data import seed_db
from .config import Config
from .extensions import db, jwt



# 🔐 garante que o médico esteja autenticado
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['JWT_SECRET_KEY'] = 'minha_nova_chave_super_secreta_SGHSS_ainda _maior'

    db.init_app(app)
    jwt.init_app(app)

    # Swagger UI
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'

    swaggerui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "SGHSS - API de Consultas"}
    )
    app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)
    
    @app.route('/')
    def index():
        return redirect('/docs')
    
    from app.routes.consultas_medico import consultas_medico_bp
    from app.routes.consultas_paciente import consultas_paciente_bp
    from app.routes.consultas_secretaria import consultas_secretaria_bp
    from app.routes.login import login_bp
    
    app.register_blueprint(consultas_medico_bp, url_prefix="/api")
    app.register_blueprint(consultas_paciente_bp, url_prefix="/api")
    app.register_blueprint(consultas_secretaria_bp, url_prefix="/api")
    app.register_blueprint(login_bp, url_prefix="/api")
    
    # Banco de dados
    with app.app_context():
        db.create_all()
        print('Tabelas verificadas e criadas se necessário!')
        seed_db(app)

    return app
    