from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from app.models.medico import Medico
from app.models.secretario import Secretario
from app.models.paciente import Paciente
from app.extensions import db

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({'erro': 'Requisição sem corpo JSON.'}), 400

    # Pega os campos com segurança (aceita minúsculas ou maiúsculas)
    nome = data.get('email') or data.get('nome') or data.get('usuario')
    senha = data.get('Senha') or data.get('senha')

    # Validação
    if not nome or not senha:
        return jsonify({'erro': 'Campos NomeSobrenome e Senha são obrigatórios.'}), 400


    # Verifica se o usuário existe em qualquer tabela
    user = (
        Medico.query.filter_by(usuario=nome, senha=senha).first() or
        Secretario.query.filter_by(usuario=nome, senha=senha).first() or
        Paciente.query.filter_by(usuario=nome, senha=senha).first()
    )

    if not user:
        return jsonify({'erro': 'Credenciais inválidas.'}), 401

    # Payload do token
    identity_data = {
        "id": user.id,
        "nome": nome,
        "nivel_acesso": user.nivel_acesso,  
        "tipo": user.__class__.__name__
    }

    # Gera o token JWT válido por 60 minutos
    access_token = 'Bearer '+ create_access_token(
        identity=identity_data,
        expires_delta=timedelta(minutes=60)
    )

    return jsonify({
        "mensagem": "Login realizado com sucesso.",
        "token": access_token,
        "expira_em": "60 minutos"
    }), 200

# Rota para editar a senha do usuário logado
@login_bp.route('/editar_senha', methods=['PUT'])   
@jwt_required() 
def editar_senha():
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    usuario_id = usuario.get('id')
    usuario_nivel = usuario.get('nivel_acesso')
    
    data = request.get_json() or {}
    
    if 'senha_atual' not in data or 'nova_senha' not in data:
        return jsonify({"erro": "Campos obrigatórios faltando. Use: senha_atual, nova_senha."}), 400    
    
    nova_senha = data['nova_senha'] 
    modelos = {
    "medico": Medico,
    "secretario": Secretario,
    "paciente": Paciente
    }

    Modelo = modelos.get(usuario_nivel)

    if not Modelo:
        return jsonify({"erro": "Nível de acesso inválido."}), 403

    usuario_obj = Modelo.query.get(usuario_id)

    if not usuario_obj:
        return jsonify({"erro": "Usuário não encontrado."}), 404

    if usuario_obj.senha != data['senha_atual'] :
        return jsonify({"erro": "Senha atual incorreta."}), 400 
    
    if usuario_obj.senha == nova_senha:
        return jsonify({"erro": "A nova senha deve ser diferente da senha atual."}), 400  
      
    usuario_obj.senha = nova_senha
    
    try:
        db.session.commit()
        return jsonify({"mensagem": "Senha atualizada com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao atualizar senha: {str(e)}"}), 500

    
                    
        