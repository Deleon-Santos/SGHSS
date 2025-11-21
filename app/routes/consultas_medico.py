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
@jwt_required() 
def finaliza_consulta(consulta_id):
    #valida o token, o nivel de acesso, a consulta, o status do paciente, status da consulta
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    
    medico_id = usuario['id']
    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'medico':
        return jsonify({"erro": "Acesso negado. Rota destinada a médicos."}), 403
    
    consulta = Consulta.query.get_or_404(consulta_id)
    if not consulta:
        return jsonify({"erro": "Consulta não encontrada."}), 404
    
    if not consulta.paciente.ativo:
        return jsonify({"erro": "Paciente inativo. Contate a secretaría."}), 403
    
    data = request.get_json() or {}
    if 'diagnostico' not in data:
        return jsonify({"erro": "Diagnóstico é obrigatório para finalizar a consulta."}), 400
    
    if consulta.medico_id != medico_id:
        return jsonify({"erro": "Ação não autorizada. Esta consulta está registrada para outro médico."}), 403
    
    if consulta.status == 'Realizada':
        return jsonify({"erro": f"Consulta {consulta_id} já foi finalizada."}), 400
    consulta.diagnostico = data['diagnostico']
    consulta.status = 'Realizada'
    consulta.medico_id = medico_id  

    db.session.commit()
    return jsonify({"mensagem": "Consulta finalizada e diagnóstico registrado", 
                                "informações" :{"Consulta_ID": consulta.id,
                                                "Medico": consulta.medico.nome, 
                                                "Paciente": consulta.paciente.nome, 
                                                "Data": str(consulta.data),
                                                "Diagnostico"  : consulta.diagnostico}}), 200


#o medico de ve prescrever uma medicação ou tratamento para uma consulta
@consultas_medico_bp.route('/consulta/<int:consulta_id>/prescreve_tratamento', methods=['POST'])
@jwt_required()  
def prescreve_medicamento(consulta_id):
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    
    medico_id = usuario['id']
    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'medico':
        return jsonify({"erro": "Acesso negado. Rota destinada a medicos."}), 403
     
    consulta = Consulta.query.get_or_404(consulta_id)
    if not consulta:
        return jsonify({"erro": "Consulta não encontrada."}), 404
    
    if not consulta.paciente.ativo:
        return jsonify({"erro": "Paciente inativo. Contate a secretaría."}), 403
    
    data = request.get_json()    
    if not all(k in data for k in ['medicacao', 'dosagem', 'orientacoes']):
        return jsonify({"erro": "Dados obrigatórios faltando ('medicacao', 'dosagem', 'orientacoes')."}), 400
    
    if consulta.medico_id != medico_id:
        return jsonify({"erro": "Ação não autorizada para este médico."}), 403
    
    if consulta.status != 'Realizada':
        return jsonify({"erro": "Medicamento só pode ser prescrito para consultas realizadas."}), 400
    medicamento = Medicamento(
        nome=data['medicacao'],
        dosagem=data['dosagem'],
        orientacoes=data.get('orientacoes'),
        consulta_id=consulta_id,
        medico_id=medico_id
    )
    db.session.add(medicamento)
    db.session.commit()
    return jsonify({"mensagem": "Medicamento prescrito com sucesso.", 
                    "medicamento":{"nome": medicamento.nome, 
                                    "dosagem": medicamento.dosagem, 
                                    "orientacoes": medicamento.orientacoes  
                                                                       }}), 201


# o medico pode solicitar um exame para uma consulta
@consultas_medico_bp.route('/consulta/<int:consulta_id>/solicita_exame', methods=['POST'])
@jwt_required()  
def solicita_exame(consulta_id):
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    
    medico_id = usuario['id']
    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'medico':
        return jsonify({"erro": "Acesso negado. Rota destinada a medicos."}), 403
    
    consulta = Consulta.query.get_or_404(consulta_id)
    if not consulta:
        return jsonify({"erro": "Consulta não encontrada."}), 404
    
    if not consulta.paciente.ativo:
        return jsonify({"erro": "Paciente inativo. Contate a secretaría."}), 403
    
    data = request.get_json() or {}

    if not data ['exame']:
        return jsonify({"erro": "Dados obrigatórios faltando ('Exame')."}), 400
    
    if consulta.medico_id != medico_id:
        return jsonify({"erro": "Ação não autorizada para este médico."}), 403
    
    if consulta.status != 'Realizada':
        return jsonify({"erro": "Exame só pode ser solicitado para consultas realizadas."}), 400
    exame = Exame(
        tipo=data['exame'],
        data_solicitacao=date.today(),
        consulta_id=consulta_id,
        medico_id=medico_id
    )
    db.session.add(exame)
    db.session.commit()
    return jsonify({"mensagem": "Exame solicitado com sucesso.", 
                    "exame":{"Exame": exame.tipo,
                            "data": exame.data_solicitacao}}), 201


#o medico pode consultar sua agenda de consultas
@consultas_medico_bp.route('/consulta/consulta_agenda_medica', methods=['GET'])
@jwt_required()  
def consulta_agenda():
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    
    medico_id = usuario['id']
    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'medico':
        return jsonify({"erro": "Acesso negado. Rota destinada a medico."}), 403
    
    data_filtro = request.args.get('data')
    query = Consulta.query.filter_by(medico_id=medico_id)
    if not query:
        return jsonify({"erro": "Consulta não encontrada."}), 404

    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter_by(data=data_obj)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    agenda = query.order_by(Consulta.data, Consulta.hora).all()

    resultado = [
        {
            "consulta_id": c.id,
            "medico_id": c.medico_id,
            "nome_medico": c.medico.nome if c.medico else None,
            "paciente": c.paciente.nome if c.paciente else None,
            "data": str(c.data),
            "hora": str(c.hora),
            "status": c.status
            
        }
        for c in agenda]
    return jsonify(resultado), 200


#o medico pode cancelar uma consulta
@consultas_medico_bp.route('/consulta/<int:consulta_id>/cancelamento_consulta', methods=['POST'])
@jwt_required()
def cancelamento_medico(consulta_id):
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    
    medico_id = usuario['id']
    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'medico':
        return jsonify({"erro": "Acesso negado. Rota destinada a medico."}), 403
    
    consulta = Consulta.query.get_or_404(consulta_id)
    if not consulta:
       return jsonify({"erro": "Consulta não encontrada."}), 404
   
    if medico_id != consulta.medico_id:
        return jsonify({"erro": f"Cancelamento autorizado apenas para o seu User_id ."}), 403
    
    if consulta.status == 'Cancelada':
        return jsonify({"erro": f"Consulta {consulta} já está cancelada."}), 400
    
    consulta.status = 'Cancelada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {consulta} cancelada com sucesso."}), 200
