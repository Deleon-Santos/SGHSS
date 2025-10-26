import os
# Adicionamos 'os' para criar o caminho absoluto do arquivo do banco de dados

# Define o diretório base do projeto
diretorio = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-forte-e-randomica'

    # --- MUDANÇA PRINCIPAL AQUI: Configuração do Banco de Dados SQLite ---
    
    # 'sqlite:///' indica que o arquivo do banco de dados está em um caminho
    # relativo ao diretório do projeto.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(diretorio, 'sghss.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False