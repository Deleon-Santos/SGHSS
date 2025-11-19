from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from werkzeug.security import check_password_hash , generate_password_hash

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

    # Aceita diferentes nomes de campo para login e senha
    nome = data.get('email') 
    senha = data.get('senha') 

    if not nome or not senha:
        return jsonify({'erro': 'Campos de login e senha são obrigatórios.'}), 400

    # Busca o usuário pelo campo 'usuario'
    user = (
        Medico.query.filter_by(usuario=nome).first() or
        Secretario.query.filter_by(usuario=nome).first() or
        Paciente.query.filter_by(usuario=nome).first()
    )

    # Se nenhum usuário encontrado
    if not user:
        return jsonify({'erro': 'Usuário não encontrado, contate a secretaria.'}), 404
    if isinstance(user, Paciente) and not user.ativo:
        return jsonify({'erro': 'Usuário inativo. Contate a secretaria.'}), 403
    
    if not check_password_hash(user.senha, senha):
        return jsonify({'erro': 'Senha incorreta.'}), 401

    identity_data = {
        "id": user.id,
        "nome": user.nome,
        "nivel_acesso": user.nivel_acesso,
        "tipo": user.__class__.__name__
    }

    
    access_token = "Bearer " + create_access_token(
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

    senha_atual = data['senha_atual']
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

    # Conferir a senha atual usando HASH
    if not check_password_hash(usuario_obj.senha, senha_atual):
        return jsonify({"erro": "Senha atual incorreta."}), 400

    # Impedir que a nova senha seja igual à atual
    if check_password_hash(usuario_obj.senha, nova_senha):
        return jsonify({"erro": "A nova senha deve ser diferente da senha atual."}), 400

    usuario_obj.senha = generate_password_hash(nova_senha)
    try:
        db.session.commit()
        return jsonify({"mensagem": "Senha atualizada com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao atualizar senha: {str(e)}"}), 500
