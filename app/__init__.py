from flask import Flask
from .config import Config
from .extensions import db



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)

    
    from .routes import consultas_bp
    app.register_blueprint(consultas_bp)

    
    with app.app_context():
        db.create_all() 
        print('Tabelas verificadas e criadas se necessário!')

    return app
