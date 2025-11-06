from datetime import date, datetime
from flask import request, jsonify, Blueprint
from app.models.medicamento import Medicamento
from app.models.consulta import Consulta
from app.models.exame import Exame
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity


consultas_medico_bp = Blueprint('consultas_medico', __name__)


@consultas_medico_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"


# Rotinas de atendimento Medico
@consultas_medico_bp.route('/consulta/<int:consulta_id>/atendimento', methods=['POST'])
@jwt_required()  # 🔐 garante que o médico esteja autenticado
def finaliza_consulta(consulta_id):
    usuario_id = get_jwt_identity()
    medico_id = usuario_id['id']
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.get_json() or {}

    # Validação do diagnóstico
    if 'diagnostico' not in data:
        return jsonify({"erro": "Diagnóstico é obrigatório para finalizar a consulta."}), 400
    
    # Verifica se o médico autenticado é o mesmo que está tentando finalizar
    if data.get('medico_id') != medico_id:
        return jsonify({"erro": "Ação não autorizada para este médico."}), 403
    
    # Atualiza os dados da consulta
    consulta.diagnostico = data['diagnostico']
    consulta.status = 'Realizada'
    consulta.medico_id = medico_id  # garante que o ID vem do token, não do body

    db.session.commit()

    return jsonify({"mensagem": f"Consulta {consulta_id} finalizada e diagnóstico registrado."}), 200


@consultas_medico_bp.route('/consulta/<int:consulta_id>/prescreve', methods=['POST'])
@jwt_required()  # 🔐 garante que o médico esteja autenticado
def prescreve_medicamento(consulta_id):
    medico_id = get_jwt_identity()
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json or {}

    if not all(k in data for k in ['nome', 'dosagem', 'medico_id']):
        return jsonify({"erro": "Dados obrigatórios faltando (nome, dosagem, medico_id)."}), 400
    
    if data['medico_id'] != medico_id:
        return jsonify({"erro": "Ação não autorizada para este médico."}), 403
    
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
@jwt_required()  # 🔐 garante que o médico esteja autenticado
def solicita_exame(consulta_id):
    medico_id = get_jwt_identity()
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json or {}

    if not all(k in data for k in ['tipo', 'medico_id']):
        return jsonify({"erro": "Dados obrigatórios faltando (tipo, medico_id)."}), 400
    if data['medico_id'] != medico_id:
        return jsonify({"erro": "Ação não autorizada para este médico."}), 403
    exame = Exame(
        tipo=data['tipo'],
        data_solicitacao=date.today(),
        consulta_id=consulta_id,
        medico_id=data['medico_id']
    )
    db.session.add(exame)
    db.session.commit()
    return jsonify({"mensagem": "Exame solicitado com sucesso.", "id": exame.id}), 201


@consultas_medico_bp.route('/consulta/agenda_medica', methods=['GET'])
@jwt_required()  # 🔐 garante que o médico esteja autenticado
def consulta_agenda():
    # ✅ Recupera o ID do médico logado do token JWT
    usuario = get_jwt_identity()
    medico_id = usuario['id']

    data_filtro = request.args.get('data')
    
    # Cria a query base filtrando pelo médico logado
    query = Consulta.query.filter_by(medico_id=medico_id)

    # Se o usuário passou um filtro de data, aplica na consulta
    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter_by(data=data_obj)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    # Ordena por data e hora
    agenda = query.order_by(Consulta.data, Consulta.hora).all()

    # Monta o resultado em JSON
    resultado = [
        {
            "consulta_id": c.medico.id,
            "medico_id": c.id,
            "nome_medico": c.medico.nome if c.medico else None,
            "paciente": c.paciente.nome if c.paciente else None,
            "data": str(c.data),
            "hora": str(c.hora),
            "status": c.status
            
        }
        for c in agenda
    ]

    return jsonify(resultado), 200
