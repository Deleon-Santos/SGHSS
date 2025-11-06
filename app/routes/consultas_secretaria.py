from datetime import date, datetime
from flask import request, jsonify, Blueprint
from app.models.consulta import Consulta
from app.extensions import db
from app.models.medico import Medico
from app.models.paciente import Paciente

consultas_secretaria_bp = Blueprint('consultas_secretaria', __name__)

@consultas_secretaria_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"


@consultas_secretaria_bp.route('/cadastra/medico', methods=['POST'])
def cadastrar_medico():
    data = request.json or {}

    if not all(k in data for k in ['nome', 'especialidade', 'crm']):
        return jsonify({"erro": "Campos obrigatórios faltando (nome, especialidade, crm)."}), 400

    medico = Medico(
        nome=data['nome'],
        especialidade=data['especialidade'],
        crm=data['crm']
    )

    db.session.add(medico)
    db.session.commit()
    return jsonify({"mensagem": f"Médico {medico.nome} cadastrado com sucesso.", "id": medico.id}), 201


# Excluir médico
@consultas_secretaria_bp.route('/consulta/medico/<int:medico_id>', methods=['DELETE'])
def excluir_medico(medico_id):
    medico = Medico.query.get_or_404(medico_id)
    db.session.delete(medico)
    db.session.commit()
    return jsonify({"mensagem": f"Médico {medico.nome} excluído com sucesso."}), 200


# Cadastrar paciente
@consultas_secretaria_bp.route('/consulta/paciente', methods=['POST'])
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
    