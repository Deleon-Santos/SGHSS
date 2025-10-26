from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from controller.Config import Config
from datetime import datetime, date

# Inicialização e Configuração do App



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
from models.BdContext import Paciente, Secretario, Medico, Consulta, Medicamento, Exame
# Importa modelos após 'db' ser inicializado
 

# --------------------------
# REQUISITO FUNCIONAL: Agendamento e Cancelamento
# --------------------------

@app.route('/consulta', methods=['POST'])
def marca_solicita_consulta():
    """Rota unificada para Marcar Consulta (Secretaria) e Solicitar Consulta (Paciente)."""
    data = request.json
    
    # Validação Básica
    if not all(k in data for k in ['data', 'hora', 'paciente_id', 'medico_id']):
        return jsonify({"erro": "Dados obrigatórios faltando (data, hora, paciente_id, medico_id)."}), 400

    # 1. Verificar disponibilidade do médico
    data_obj = datetime.strptime(data['data'], '%Y-%m-%d').date()
    hora_obj = datetime.strptime(data['hora'], '%H:%M').time()

    consulta_existente = Consulta.query.filter_by(
        medico_id=data['medico_id'], 
        data=data_obj, 
        hora=hora_obj,
        status='Agendada' # Apenas consultas agendadas contam para indisponibilidade
    ).first()

    if consulta_existente:
        return jsonify({"erro": "Médico já possui consulta agendada neste horário."}), 409

    # 2. Determinar o agendador (Secretaria ou Paciente)
    secretario_id = data.get('secretario_id') # Presente se for agendado pela Secretária
    
    nova_consulta = Consulta(
        data=data_obj,
        hora=hora_obj,
        paciente_id=data['paciente_id'],
        medico_id=data['medico_id'],
        secretario_id=secretario_id
    )

    db.session.add(nova_consulta)
    db.session.commit()
    return jsonify({"mensagem": "Consulta agendada/solicitada com sucesso!", "id": nova_consulta.id}), 201


@app.route('/consulta/<int:consulta_id>/cancelar', methods=['PUT'])
def cancela_solicita_cancelamento_consulta(consulta_id):
    """Rota para Cancelar Consulta (Secretaria) ou Solicitar Cancelamento (Paciente)."""
    consulta = Consulta.query.get_or_404(consulta_id)

    if consulta.status == 'Realizada':
        return jsonify({"erro": "Não é possível cancelar uma consulta já realizada."}), 400
        
    consulta.status = 'Cancelada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {consulta_id} cancelada com sucesso."}), 200

# --------------------------
# REQUISITO FUNCIONAL: Gestão da Consulta (Médico)
# --------------------------

@app.route('/consulta/<int:consulta_id>/realiza', methods=['PUT'])
def realiza_consulta(consulta_id):
    """Implementa o caso de uso 'Realiza Consulta'."""
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json
    
    if 'diagnostico' not in data:
        return jsonify({"erro": "Diagnóstico é obrigatório para finalizar a consulta."}), 400

    consulta.diagnostico = data['diagnostico']
    consulta.status = 'Realizada'
    db.session.commit()
    return jsonify({"mensagem": f"Consulta {consulta_id} finalizada e diagnóstico registrado."}), 200

@app.route('/consulta/<int:consulta_id>/prescreve', methods=['POST'])
def prescreve_medicamento(consulta_id):
    """Implementa o caso de uso 'Prescreve Medicamento'."""
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json
    
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

@app.route('/consulta/<int:consulta_id>/solicita_exame', methods=['POST'])
def solicita_exame(consulta_id):
    """Implementa o caso de uso 'Solicita Exame'."""
    consulta = Consulta.query.get_or_404(consulta_id)
    data = request.json
    
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


# --------------------------
# REQUISITO FUNCIONAL: Consulta Agenda (Secretaria)
# --------------------------

@app.route('/agenda/medico/<int:medico_id>', methods=['GET'])
def consulta_agenda(medico_id):
    """Implementa o caso de uso 'Consulta Agenda'."""
    
    # Filtro opcional por data
    data_filtro = request.args.get('data')
    
    query = Consulta.query.filter_by(medico_id=medico_id)

    if data_filtro:
        try:
            data_obj = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter_by(data=data_obj)
        except ValueError:
            return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    agenda = query.order_by(Consulta.data, Consulta.hora).all()
    
    resultado = [{
        "id": c.id,
        "paciente": c.paciente.nome,
        "data": str(c.data),
        "hora": str(c.hora),
        "status": c.status
    } for c in agenda]
    
    return jsonify(resultado), 200

# --------------------------
# FUNÇÕES DE INICIALIZAÇÃO
# --------------------------

@app.cli.command("init-db")
def init_db():
    """Cria as tabelas no banco de dados."""
    with app.app_context():
        db.create_all()
        print("Tabelas criadas no banco de dados!")


if __name__ == '__main__':
    # Você precisará configurar seu banco de dados PostgreSQL
    # e rodar 'flask init-db' antes de iniciar o app.
    app.run(debug=True)