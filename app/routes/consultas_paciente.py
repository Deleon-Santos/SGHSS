from datetime import date, datetime
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.consulta import Consulta
from app.extensions import db
from app.models.medico import Medico



consultas_paciente_bp = Blueprint('consultas_paciente', __name__)

@consultas_paciente_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"


# o paciente pode agendar uma consulta
@consultas_paciente_bp.route('/consulta/novo_agendamento', methods=['POST'])
@jwt_required()
def agendamento():
    paciente_id = get_jwt_identity()
    data = request.json or {}
    if not paciente_id :
        return jsonify({"erro": "Paciente não identificado."}), 403
    
    if not all(k in data for k in ['medico_id', 'data', 'hora']):
        return jsonify({"erro": "Dados obrigatórios faltando (medico_id, data, hora)."}), 400
    
    if paciente_id != data.get('paciente_id'):
        return jsonify({"erro": f"Agendamento autrizado apena para o seu User_id."}), 403
    
    try:
        data_consulta = datetime.strptime(data['data'], '%Y-%m-%d').date()
        hora_consulta = datetime.strptime(data['hora'], '%H:%M').time()
    except ValueError:
        return jsonify({"erro": "Formato de data ou hora inválido."}), 400

    consulta = Consulta(
        paciente_id=paciente_id,
        medico_id=data['medico_id'],
        data=data_consulta,
        hora=hora_consulta,
        status='Agendada'
    )
    db.session.add(consulta)
    db.session.commit()
    return jsonify({"mensagem": "Consulta agendada com sucesso.", "id": consulta.id}), 201


# o paciente pode ver a lista de medicos credenciados
@consultas_paciente_bp.route('/consulta/lista_medico_credenciado', methods=['GET'])
@jwt_required()
def consulta_lista_medico_credenciado():
    paciente_id = get_jwt_identity()
    if not paciente_id:
        return jsonify({"erro": "Paciente não identificado."}), 403

    medicos = Medico.query.all()

    lista_medicos = []
    for medico in medicos:
        lista_medicos.append({
            "id": medico.id,
            "nome": medico.nome,
            "crm": medico.crm,
            "especialidade": medico.especialidade,
        })

    return jsonify(lista_medicos), 200
   

# O parciente deve verificar a ajenda do medico de acordo com a especialidade
@consultas_paciente_bp.route('/consulta/agenda_medica/<int:medico_id>', methods=['GET'])
@jwt_required()
def consulta_agenda_especialidade(medico_id):
    paciente_id = get_jwt_identity()
    if not paciente_id:
        return jsonify({"erro": "Paciente não identificado."}), 403
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

@consultas_paciente_bp.route('/consulta/agendamento_paciente', methods=['GET'])
@jwt_required()
def consulta_agendamento():
    paciente_id = get_jwt_identity()
    
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

#o paciente pode cancelar uma consulta
@consultas_paciente_bp.route('/consulta/<int:consulta_id>/cancelamento', methods=['POST'])
@jwt_required()
def cancelamento(consulta_id):
    paciente_id = get_jwt_identity()
    data = request.json or {}
    consulta = Consulta.query.get_or_404(consulta_id)

    if 'consulta_id' not in data:
        return jsonify({"erro": "consulta_id é obrigatório para cancelar a consulta."}), 400
    
    if paciente_id != data.get('paciente_id'):
        return jsonify({"erro": f"Cancelamento autorizado apenas para o seu User_id {paciente_id}."}), 403
    
    consulta = Consulta.query.get_or_404(data['consulta_id'])
    consulta.status = 'Cancelada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {data['consulta_id']} cancelada com sucesso."}), 200


# o paciente pode ver sua agenda de consultas
