from datetime import date, datetime
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import consulta
from app.models.consulta import Consulta
from app.extensions import db
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.secretario import Secretario

consultas_secretaria_bp = Blueprint('consultas_secretaria', __name__)

@consultas_secretaria_bp.route('/')
def swagger_redirect():
    return "<meta http-equiv='refresh' content='0;url=/'>"

# Cadstrar uma novo medico é permitido apenas a membros da secretaria
@consultas_secretaria_bp.route('/cadastra/novo_medico', methods=['POST'])
@jwt_required()
def cadastrar_medico():
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    
    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'secretario':
        return jsonify({"erro": "Acesso negado. Apenas secretários podem cadastrar médicos."}), 403
  
    data = request.get_json() or {}
    if not data:
        return jsonify({"erro": "Nenhum dado fornecido."}), 400
        
    campos_obrigatorios = ['nome', 'especialidade', 'crm', 'email', 'senha' ]
    if not all(campo in data for campo in campos_obrigatorios):
        return jsonify({
            "erro": "Campos obrigatórios faltando. Use: nome, especialidade, crm, email, senha."
        }), 400

    if Medico.query.filter_by(crm=data['crm']).first():
        return jsonify({"erro": "Já existe um médico cadastrado com este CRM."}), 400

    novo_medico = Medico(
        nome=data['nome'],
        especialidade=data['especialidade'],
        crm=data['crm'],
        usuario=data['email'],
        senha=data['senha'],
        nivel_acesso='medico'
    )

    db.session.add(novo_medico)
    db.session.commit()

    return jsonify({
        "mensagem": "Um novo médico foi cadastrado com sucesso.",
        "id": novo_medico.id,
        "nome": novo_medico.nome,
        "especialidade": novo_medico.especialidade, 
        "crm": novo_medico.crm
    }), 201


# Excluir médico
@consultas_secretaria_bp.route('/deleta/medico/<int:medico_id>', methods=['DELETE'])
@jwt_required()
def excluir_medico(medico_id):
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403

    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'secretario':
        return jsonify({"erro": "Acesso negado. Rota destinada a secretarios."}), 403
    medico = Medico.query.get_or_404(medico_id)
    if not medico:
        return jsonify({"erro": "Médico não encontrado."}), 404
    db.session.delete(medico)
    db.session.commit()
    return jsonify({"mensagem": f"Médico {medico.nome} excluído com sucesso."}), 200


# Cadastrar paciente
@consultas_secretaria_bp.route('/cadastra/paciente', methods=['POST'])
@jwt_required()
def cadastrar_paciente():
    data = request.get_json() or {}
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403

    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'secretario':
        return jsonify({"erro": "Acesso negado. Rota destinada a secretarios."}), 403
    
    if not all(k in data for k in ['nome', 'cpf', 'data_nascimento','email','senha']):
        return jsonify({"erro": "Campos obrigatórios faltando (nome, cpf, data_nascimento, email, senha)."}), 400
    
    if Paciente.query.filter_by(cpf=data['cpf']).first():
        return jsonify({"erro": "Já existe um paciente cadastrado com este CPF."}), 400
    try:
        data_nasc = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    paciente = Paciente(
        nome=data['nome'],
        cpf=data['cpf'],
        data_nascimento=data_nasc,
        usuario=data['email'],
        senha=data['senha'],
        nivel_acesso='paciente'
    )

    db.session.add(paciente)
    db.session.commit()
    return jsonify({"mensagem": " um novo Paciente foi cadastrado com sucesso.", 
                    "id": paciente.id,
                    "nome":paciente.nome,
                    }), 201


# Excluir paciente
@consultas_secretaria_bp.route('/deleta/paciente/<int:paciente_id>', methods=['DELETE'])
@jwt_required()
def excluir_paciente(paciente_id):
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403

    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'secretario':
        return jsonify({"erro": "Acesso negado. Rota destinada a secretarios."}), 403
    
    paciente = Paciente.query.get_or_404(paciente_id)
    if not paciente:
        return jsonify({"erro": "Paciente não encontrado."}), 404
    db.session.delete(paciente)
    db.session.commit()
    return jsonify({"mensagem": f"Paciente {paciente.nome} excluído com sucesso."}), 200


# Ver todas as consultas agendadas
@consultas_secretaria_bp.route('/consulta/consultas_geral_marcadas', methods=['GET'])
@jwt_required()
def ver_consultas_agendadas():
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403

    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'secretario':
        return jsonify({"erro": "Acesso negado. Rota destinada a secretarios."}), 403
    
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

@consultas_secretaria_bp.route('/consulta/cadastro_geral_usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403

    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'secretario':
        return jsonify({"erro": "Acesso negado. Acesso negado. Rota destinada a secretarios."}), 403
    
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

# Obter detalhes de uma consulta por ID
@consultas_secretaria_bp.route('/consulta/<int:consulta_id>/', methods=['GET'])
@jwt_required() 
def consulta_por_id(consulta_id):
    usuario = get_jwt_identity() or {}
    if not usuario:
        return jsonify({"erro": "Usuário não identificado ou token inválido."}), 403
    
    
    usuario_nivel = usuario.get('nivel_acesso')
    if usuario_nivel != 'secretario':
        return jsonify({"erro": "Acesso negado. Rota destinada a secretarios."}), 403
    
    consulta = Consulta.query.get_or_404(consulta_id)
    if not consulta:
        return jsonify({"erro": "Consulta não encontrada."}), 404
    
    task_list = {
        "consulta_id": consulta.id,
        "paciente": consulta.paciente.nome if consulta.paciente else None,
        "medico": consulta.medico.nome if consulta.medico else None,
        "data": str(consulta.data),
        "hora": str(consulta.hora),
        "status": consulta.status
    }
    return jsonify({"Consulta":task_list}), 200  
   
    