from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app.models.medico import Medico
from app.models.secretario import Secretario
from app.models.paciente import Paciente
from app.extensions import db

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # if not data:
    #     return jsonify({'erro': 'Requisição sem corpo JSON.'}), 400

    # # Pega os campos com segurança (aceita minúsculas ou maiúsculas)
    # nome = data.get('NomeSobrenome') or data.get('nome') or data.get('usuario')
    # senha = data.get('Senha') or data.get('senha')

    # # Validação
    # if not nome or not senha:
    #     return jsonify({'erro': 'Campos NomeSobrenome e Senha são obrigatórios.'}), 400


    # # Verifica se o usuário existe em qualquer tabela
    # user = (
    #     Medico.query.filter_by(usuario=nome, senha=senha).first() or
    #     Secretario.query.filter_by(usuario=nome, senha=senha).first() or
    #     Paciente.query.filter_by(usuario=nome, senha=senha).first()
    # )

    # if not user:
    #     return jsonify({'erro': 'Credenciais inválidas.'}), 401

    # # Payload do token
    # identity_data = {
    #     "id": user.id,
    #     "nome": nome,
    #     "tipo": user.__class__.__name__
    # }

    # # Gera o token JWT válido por 60 minutos
    # access_token = create_access_token(
    #     identity=identity_data,
    #     expires_delta=timedelta(minutes=60)
    # )

    # return jsonify({
    #     "mensagem": "Login realizado com sucesso.",
    #     "token": access_token,
    #     "expira_em": "60 minutos"
    # }), 200
    data = request.get_json(silent=True)
    print("\n=== DEBUG LOGIN ===")
    print("Tipo de conteúdo:", request.content_type)
    print("Corpo cru:", request.data)
    print("JSON interpretado:", data)
    print("===================\n")

    if not data:
        return jsonify({'erro': 'Requisição sem corpo JSON.'}), 400

    nome = data.get('NomeSobrenome') or data.get('nome') or data.get('usuario')
    senha = data.get('Senha') or data.get('senha')

    if not nome or not senha:
        return jsonify({'erro': 'Campos NomeSobrenome e Senha são obrigatórios.'}), 400

    return jsonify({
        "mensagem": "Debug OK!",
        "nome": nome,
        "senha": senha
    }), 200