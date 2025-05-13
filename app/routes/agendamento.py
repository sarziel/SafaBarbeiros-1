from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Agendamento, PerfilBarbeiro, Servico
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

agendamento_bp = Blueprint('agendamento', __name__, url_prefix='/agendamento')

@agendamento_bp.route('/horarios-disponiveis')
@login_required
def horarios_disponiveis():
    """
    Endpoint para buscar horários disponíveis de um barbeiro em uma data específica.
    Parâmetros:
    - barbeiro_id: ID do barbeiro
    - data: Data no formato YYYY-MM-DD
    - servico_id: ID do serviço (para calcular a duração)
    """
    barbeiro_id = request.args.get('barbeiro_id', type=int)
    data_str = request.args.get('data')
    servico_id = request.args.get('servico_id', type=int)
    
    if not barbeiro_id or not data_str or not servico_id:
        return jsonify({'status': 'error', 'message': 'Parâmetros inválidos'}), 400
    
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Formato de data inválido'}), 400
    
    # Obter perfil do barbeiro
    perfil = PerfilBarbeiro.query.filter_by(user_id=barbeiro_id).first()
    if not perfil:
        return jsonify({'status': 'error', 'message': 'Barbeiro não encontrado'}), 404
    
    # Verificar se o barbeiro trabalha nesse dia da semana
    dia_semana = str(data.weekday() + 1)  # +1 porque no banco 1=segunda, 7=domingo
    if dia_semana not in perfil.dias_trabalho.split(','):
        return jsonify({'horarios': [], 'message': 'O barbeiro não trabalha neste dia da semana'})
    
    # Obter serviço para calcular duração
    servico = Servico.query.get(servico_id)
    if not servico:
        return jsonify({'status': 'error', 'message': 'Serviço não encontrado'}), 404
    
    duracao = servico.duracao
    
    # Obter horários de trabalho do barbeiro
    hora_inicio = perfil.horario_inicio
    hora_fim = perfil.horario_fim
    
    # Obter agendamentos existentes nessa data
    agendamentos = Agendamento.query.filter(
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.data == data,
        Agendamento.status != 'cancelado'
    ).all()
    
    # Listar horários ocupados
    horarios_ocupados = []
    for a in agendamentos:
        inicio = datetime.combine(data, a.hora_inicio)
        fim = datetime.combine(data, a.hora_fim)
        horarios_ocupados.append((inicio, fim))
    
    # Gerar horários disponíveis em intervalos de 30 minutos
    horarios_disponiveis = []
    tempo_atual = datetime.combine(data, hora_inicio)
    tempo_limite = datetime.combine(data, hora_fim)
    
    while tempo_atual < tempo_limite:
        tempo_fim = tempo_atual + timedelta(minutes=duracao)
        
        # Verificar se o horário está dentro do horário de trabalho
        if tempo_fim.time() <= hora_fim:
            # Verificar se o horário não conflita com agendamentos existentes
            disponivel = True
            for inicio, fim in horarios_ocupados:
                if (tempo_atual >= inicio and tempo_atual < fim) or \
                   (tempo_fim > inicio and tempo_fim <= fim) or \
                   (tempo_atual <= inicio and tempo_fim >= fim):
                    disponivel = False
                    break
            
            if disponivel:
                horarios_disponiveis.append(tempo_atual.strftime('%H:%M'))
        
        tempo_atual += timedelta(minutes=30)
    
    return jsonify({'horarios': horarios_disponiveis})

@agendamento_bp.route('/servicos-barbeiro/<int:barbeiro_id>')
@login_required
def servicos_barbeiro(barbeiro_id):
    """
    Endpoint para buscar serviços oferecidos por um barbeiro.
    """
    perfil = PerfilBarbeiro.query.filter_by(user_id=barbeiro_id).first()
    if not perfil:
        return jsonify({'status': 'error', 'message': 'Barbeiro não encontrado'}), 404
    
    servicos = Servico.query.filter_by(barbeiro_id=perfil.id, ativo=True).all()
    
    servicos_list = [
        {
            'id': s.id,
            'nome': s.nome,
            'descricao': s.descricao,
            'preco': float(s.preco),
            'duracao': s.duracao
        }
        for s in servicos
    ]
    
    return jsonify({'servicos': servicos_list})
