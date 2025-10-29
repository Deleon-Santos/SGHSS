from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from app.database.data import seed_db
from .config import Config
from .extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Swagger UI
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'

    swaggerui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "SGHSS - API de Consultas"}
    )
    app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)

    # ✅ Registrar rotas
    from app.routes.consultas import consultas_bp
    app.register_blueprint(consultas_bp, url_prefix="/api")

    # Banco de dados
    with app.app_context():
        db.create_all()
        print('Tabelas verificadas e criadas se necessário!')
        seed_db(app)

    return app
