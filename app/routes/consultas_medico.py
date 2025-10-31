from datetime import date, datetime
from flask import request, jsonify, Blueprint
from app.models.medicamento import Medicamento
from app.models.consulta import Consulta
from app.models.exame import Exame
from app.extensions import db



consultas_medico_bp = Blueprint('consultas_medico', __name__)


@consultas_medico_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"


# Rotinas de atendimento Medico
@consultas_medico_bp.route('/consulta/<int:consulta_id>/atendimento', methods=['POST'])
def finaliza_consulta(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json or {}

    if 'diagnostico' not in data:
        return jsonify({"erro": "Diagnóstico é obrigatório para finalizar a consulta."}), 400

    consulta.diagnostico = data['diagnostico']
    consulta.status = 'Realizada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {consulta_id} finalizada e diagnóstico registrado."}), 200


@consultas_medico_bp.route('/consulta/<int:consulta_id>/prescreve', methods=['POST'])
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


@consultas_medico_bp.route('/consulta/<int:consulta_id>/solicita_exame', methods=['POST'])
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


@consultas_medico_bp.route('/agenda/medico/<int:medico_id>', methods=['GET'])
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





