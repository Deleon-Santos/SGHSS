from datetime import date, datetime
from flask import request, jsonify, Blueprint
from app.models.consulta import Consulta
from app.extensions import db



consultas_paciente_bp = Blueprint('consultas_paciente', __name__)

@consultas_paciente_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"

# O parciente deve verificar a ajenda do medico de acordo com a especialidade
@consultas_paciente_bp.route('/agenda/_especialidade/<int:medico_id>', methods=['GET'])
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
@consultas_paciente_bp.route('/consulta/agendamento', methods=['POST'])
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
@consultas_paciente_bp.route('/consulta/<int:consulta_id>/cancelamento', methods=['POST'])
def cancelamento():
    data = request.json or {}

    if 'consulta_id' not in data:
        return jsonify({"erro": "consulta_id é obrigatório para cancelar a consulta."}), 400

    consulta = Consulta.query.get_or_404(data['consulta_id'])
    consulta.status = 'Cancelada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {data['consulta_id']} cancelada com sucesso."}), 200


# o paciente pode ver sua agenda de consultas
@consultas_paciente_bp.route('/agenda/paciente', methods=['GET'])
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
