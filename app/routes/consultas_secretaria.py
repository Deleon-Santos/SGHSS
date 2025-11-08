from datetime import date, datetime
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.consulta import Consulta
from app.extensions import db
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.secretario import Secretario

consultas_secretaria_bp = Blueprint('consultas_secretaria', __name__)

@consultas_secretaria_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"

@consultas_secretaria_bp.route('/cadastra/medico', methods=['POST'])
@jwt_required()
def cadastrar_medico():
    data = request.get_json() or {}
    usuario = get_jwt_identity()
    secretario_matricula = usuario['matricula']
    secretario_matricula = usuario.get('matricula')
    if not secretario_matricula:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403

    # 🔹 Verifica diretamente se existe no banco
    secretario = Secretario.query.filter_by(matricula=secretario_matricula).first()
    if not secretario:
        return jsonify({"erro": "Acesso negado. Apenas secretários podem cadastrar médicos."}), 403

    campos_obrigatorios = ['nome', 'especialidade', 'crm', 'usuario', 'senha']
    if not all(campo in data for campo in campos_obrigatorios):
        return jsonify({
            "erro": "Campos obrigatórios faltando. Use: nome, especialidade, crm, usuario, senha."
        }), 400

    if Medico.query.filter_by(crm=data['crm']).first():
        return jsonify({"erro": "Já existe um médico cadastrado com este CRM."}), 400

    novo_medico = Medico(
        nome=data['nome'],
        especialidade=data['especialidade'],
        crm=data['crm'],
        usuario=data['usuario'],
        senha=data['senha']
    )

    db.session.add(novo_medico)
    db.session.commit()

    return jsonify({
        "mensagem": f"Médico {novo_medico.nome} cadastrado com sucesso.",
        "id": novo_medico.id
    }), 201


# Excluir médico
@consultas_secretaria_bp.route('/consulta/medico/<int:medico_id>', methods=['DELETE'])
def excluir_medico(medico_id):
    medico = Medico.query.get_or_404(medico_id)
    db.session.delete(medico)
    db.session.commit()
    return jsonify({"mensagem": f"Médico {medico.nome} excluído com sucesso."}), 200


# Cadastrar paciente
@consultas_secretaria_bp.route('/cadastra/paciente', methods=['POST'])
def cadastrar_paciente():
    data = request.json or {}

    if not all(k in data for k in ['nome', 'cpf', 'data_nascimento']):
        return jsonify({"erro": "Campos obrigatórios faltando (nome, cpf, data_nascimento)."}), 400

    try:
        data_nasc = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    paciente = Paciente(
        nome=data['nome'],
        cpf=data['cpf'],
        data_nascimento=data_nasc
    )

    db.session.add(paciente)
    db.session.commit()
    return jsonify({"mensagem": f"Paciente {paciente.nome} cadastrado com sucesso.", "id": paciente.id}), 201


# Excluir paciente
@consultas_secretaria_bp.route('/consulta/paciente/<int:paciente_id>', methods=['DELETE'])
def excluir_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    db.session.delete(paciente)
    db.session.commit()
    return jsonify({"mensagem": f"Paciente {paciente.nome} excluído com sucesso."}), 200


# Ver todas as consultas agendadas
@consultas_secretaria_bp.route('/consulta/consultas_marcadas', methods=['GET'])
def ver_consultas_agendadas():
    status_filtro = request.args.get('status')  # opcional: Agendada, Realizada, Cancelada
    query = Consulta.query

    if status_filtro:
        query = query.filter_by(status=status_filtro)

    consultas = query.order_by(Consulta.data, Consulta.hora).all()

    resultado = [
        {
            "id": c.id,
            "paciente": c.paciente.nome if c.paciente else None,
            "medico": c.medico.nome if c.medico else None,
            "data": str(c.data),
            "hora": str(c.hora),
            "status": c.status
        }
        for c in consultas
    ]

    return jsonify(resultado), 200

@consultas_secretaria_bp.route('/consulta/cadastro_usuarios', methods=['GET'])
#@jwt_required()
def listar_usuarios():
    
    tipo_filtro = request.args.get('tipo')

    resultado = []

    # 🔹 Filtra e busca conforme o tipo informado
    if tipo_filtro == 'paciente' or not tipo_filtro:
        pacientes = Paciente.query.order_by(Paciente.nome).all()
        resultado.extend([
            {
                "id": p.id,
                "nome": p.nome,
                "cpf": p.cpf,
                "usuario": getattr(p, "usuario", None),
                "tipo": "paciente"
            }
            for p in pacientes
        ])
    

    if tipo_filtro == 'medico' or not tipo_filtro:
        medicos = Medico.query.order_by(Medico.nome).all()
        resultado.extend([
            {
                "id": m.id,
                "nome": m.nome,
                "crm": m.crm,
                "especialidade": m.especialidade,
                "usuario": getattr(m, "usuario", None),
                "tipo": "medico"
            }
            for m in medicos
        ])

    if tipo_filtro == 'secretaria' or not tipo_filtro:
        secretarias = Secretario.query.order_by(Secretario.nome).all()
        resultado.extend([
            {
                "id": s.id,
                "nome": s.nome,
                "matricula": s.matricula,
                "usuario": getattr(s, "usuario", None),
                "tipo": "secretaria"
            }
            for s in secretarias
        ])
    if not resultado:
        return jsonify({"mensagem": "Nenhum usuário encontrado para o tipo especificado."}), 404
    return jsonify({"menssagem":resultado}), 200
