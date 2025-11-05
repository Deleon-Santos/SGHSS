from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.medico import Medico
from app.models.secretario import Secretario
from app.models.paciente import Paciente

novo_usuario_bp = Blueprint('login_usuario', __name__)
@novo_usuario_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    tipo = data.get('tipo')  # 'medico', 'paciente' ou 'secretaria'
    usuario = data.get('usuario')
    senha = data.get('senha')

    if not all([tipo, usuario, senha]):
        return jsonify({"erro": "Campos obrigatórios faltando."}), 400

    # 🔍 Verifica o tipo de login
    if tipo == 'medico':
        user = Medico.query.filter_by(usuario=usuario, senha=senha).first()
    elif tipo == 'paciente':
        user = Paciente.query.filter_by(usuario=usuario, senha=senha).first()
    elif tipo == 'secretaria':
        user = Secretario.query.filter_by(usuario=usuario, senha=senha).first()
    else:
        return jsonify({"erro": "Tipo de usuário inválido."}), 400

    if not user:
        return jsonify({"erro": "Credenciais inválidas."}), 401

    # ✅ Cria o token com a identidade e tipo de usuário
    token = create_access_token(identity={"id": user.id, "tipo": tipo})

    return jsonify(access_token=token), 200
