from datetime import date, datetime
from flask import request, jsonify, Blueprint
from app.models.medicamento import Medicamento
from app.models.consulta import Consulta
from app.models.exame import Exame
from app.extensions import db
from app.models.medico import Medico
from app.models.paciente import Paciente


consultas_bp = Blueprint('consultas', __name__)


@consultas_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"


# Rotinas de atendimento Medico
@consultas_bp.route('/consulta/<int:consulta_id>/atendimento', methods=['POST'])
def finaliza_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json or {}

    if 'diagnostico' not in data:
        return jsonify({"erro": "Diagnóstico é obrigatório para finalizar a consulta."}), 400

    consulta.diagnostico = data['diagnostico']
    consulta.status = 'Realizada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {consulta_id} finalizada e diagnóstico registrado."}), 200


@consultas_bp.route('/consulta/<int:consulta_id>/prescreve', methods=['POST'])
def prescreve_medicamento(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json or {}

    if not all(k in data for k in ['nome', 'dosagem', 'medico_id']):
        return jsonify({"erro": "Dados obrigatórios faltando (nome, dosagem, medico_id)."}), 400

    medicamento = Medicamento(
        nome=data['nome'],
        dosagem=data['dosagem'],
        orientacoes=data.get('orientacoes'),
        consulta_id=consulta_id,
        medico_id=data['medico_id']
    )
    db.session.add(medicamento)
    db.session.commit()
    return jsonify({"mensagem": "Medicamento prescrito com sucesso.", "id": medicamento.id}), 201


@consultas_bp.route('/consulta/<int:consulta_id>/solicita_exame', methods=['POST'])
def solicita_exame(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json or {}

    if not all(k in data for k in ['tipo', 'medico_id']):
        return jsonify({"erro": "Dados obrigatórios faltando (tipo, medico_id)."}), 400

    exame = Exame(
        tipo=data['tipo'],
        data_solicitacao=date.today(),
        consulta_id=consulta_id,
        medico_id=data['medico_id']
    )
    db.session.add(exame)
    db.session.commit()
    return jsonify({"mensagem": "Exame solicitado com sucesso.", "id": exame.id}), 201


@consultas_bp.route('/agenda/medico/<int:medico_id>', methods=['GET'])
def consulta_agenda(medico_id):
    data_filtro = request.args.get('data')
    query = Consulta.query.filter_by(medico_id=medico_id)

    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter_by(data=data_obj)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    agenda = query.order_by(Consulta.data, Consulta.hora).all()

    resultado = [
        {
            "id": c.id,
            "paciente": c.paciente.nome if c.paciente else None,
            "data": str(c.data),
            "hora": str(c.hora),
            "status": c.status
        }
        for c in agenda
    ]

    return jsonify(resultado), 200


#==============Rotinas de agendamento de consultas do Cliente==============

# O parciente deve verificar a ajenda do medico de acordo com a especialidade
@consultas_bp.route('/agenda/_especialidade/<int:medico_id>', methods=['GET'])
def consulta_agenda_especialidade(medico_id):
    data_filtro = request.args.get('data')
    query = Consulta.query.filter_by(medico_id=medico_id)

    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter_by(data=data_obj)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    agenda = query.order_by(Consulta.data, Consulta.hora).all()

    resultado = [
        {
            "id": c.id,
            "data": str(c.data),
            "hora": str(c.hora),
            "status": c.status
        }
        for c in agenda
    ]
    return jsonify(resultado), 200


# o paciente pode agendar uma consulta
@consultas_bp.route('/consulta/agendamento', methods=['POST'])
def agendamento():
    data = request.json or {}

    if not all(k in data for k in ['paciente_id', 'medico_id', 'data', 'hora']):
        return jsonify({"erro": "Dados obrigatórios faltando (paciente_id, medico_id, data, hora)."}), 400

    try:
        data_consulta = datetime.strptime(data['data'], '%Y-%m-%d').date()
        hora_consulta = datetime.strptime(data['hora'], '%H:%M').time()
    except ValueError:
        return jsonify({"erro": "Formato de data ou hora inválido."}), 400

    consulta = Consulta(
        paciente_id=data['paciente_id'],
        medico_id=data['medico_id'],
        data=data_consulta,
        hora=hora_consulta,
        status='Agendada'
    )
    db.session.add(consulta)
    db.session.commit()
    return jsonify({"mensagem": "Consulta agendada com sucesso.", "id": consulta.id}), 201


#o paciente pode cancelar uma consulta
@consultas_bp.route('/consulta/<int:consulta_id>/cancelamento', methods=['POST'])
def cancelamento():
    data = request.json or {}

    if 'consulta_id' not in data:
        return jsonify({"erro": "consulta_id é obrigatório para cancelar a consulta."}), 400

    consulta = Consulta.query.get_or_404(data['consulta_id'])
    consulta.status = 'Cancelada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {data['consulta_id']} cancelada com sucesso."}), 200


# o paciente pode ver sua agenda de consultas
@consultas_bp.route('/agenda/paciente', methods=['GET'])
def consulta_agendamento(paciente_id):
    data_filtro = request.args.get('data')
    query = Consulta.query.filter_by(paciente_id=paciente_id)

    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter_by(data=data_obj)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    agenda = query.order_by(Consulta.data, Consulta.hora).all()

    resultado = [
        {
            "id": c.id,
            "medico": c.medico.nome if c.medico else None,
            "data": str(c.data),
            "hora": str(c.hora),
            "status": c.status
        }
        for c in agenda
    ]

    return jsonify(resultado), 200


@consultas_bp.route('/consulta/medico', methods=['POST'])
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
@consultas_bp.route('/consulta/medico/<int:medico_id>', methods=['DELETE'])
def excluir_medico(medico_id):
    medico = Medico.query.get_or_404(medico_id)
    db.session.delete(medico)
    db.session.commit()
    return jsonify({"mensagem": f"Médico {medico.nome} excluído com sucesso."}), 200


# Cadastrar paciente
@consultas_bp.route('/consulta/paciente', methods=['POST'])
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
@consultas_bp.route('/consulta/paciente/<int:paciente_id>', methods=['DELETE'])
def excluir_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    db.session.delete(paciente)
    db.session.commit()
    return jsonify({"mensagem": f"Paciente {paciente.nome} excluído com sucesso."}), 200


# Ver todas as consultas agendadas
@consultas_bp.route('/consulta/consultas', methods=['GET'])
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
    