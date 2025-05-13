from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import PerfilBarbeiro, Venda, ItemVenda, Servico
from datetime import datetime, timedelta
from sqlalchemy import func

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')

@financeiro_bp.route('/dados-relatorio')
@login_required
def dados_relatorio():
    """
    Retorna dados para relatórios financeiros.
    Parâmetros:
    - data_inicio: Data inicial no formato YYYY-MM-DD
    - data_fim: Data final no formato YYYY-MM-DD
    """
    if not current_user.is_barbeiro():
        return jsonify({'status': 'error', 'message': 'Acesso negado'}), 403
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        return jsonify({'status': 'error', 'message': 'Perfil não encontrado'}), 404
    
    # Obter datas do período
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        hoje = datetime.now().date()
        data_inicio = hoje - timedelta(days=hoje.weekday())  # Início da semana
        data_fim = hoje
    
    # Dados para gráfico de vendas por forma de pagamento
    vendas_por_pagamento = db.session.query(
        Venda.forma_pagamento,
        func.sum(Venda.valor_total).label('total')
    ).filter(
        Venda.barbeiro_id == perfil.id,
        Venda.data >= data_inicio,
        Venda.data <= data_fim
    ).group_by(Venda.forma_pagamento).all()
    
    # Dados para gráfico de vendas por serviço
    vendas_por_servico = db.session.query(
        Servico.nome,
        func.sum(ItemVenda.valor_total).label('total')
    ).join(
        ItemVenda, Servico.id == ItemVenda.servico_id
    ).join(
        Venda, ItemVenda.venda_id == Venda.id
    ).filter(
        Venda.barbeiro_id == perfil.id,
        Venda.data >= data_inicio,
        Venda.data <= data_fim
    ).group_by(Servico.nome).all()
    
    # Dados para gráfico de vendas por dia
    vendas_por_dia = db.session.query(
        func.date(Venda.data).label('dia'),
        func.sum(Venda.valor_total).label('total')
    ).filter(
        Venda.barbeiro_id == perfil.id,
        Venda.data >= data_inicio,
        Venda.data <= data_fim
    ).group_by(func.date(Venda.data)).all()
    
    # Calcular totais
    total_vendas = sum(venda[1] for venda in vendas_por_pagamento)
    total_servicos = len(vendas_por_servico)
    
    return jsonify({
        'vendas_por_pagamento': [
            {'forma': forma, 'total': float(total)} 
            for forma, total in vendas_por_pagamento
        ],
        'vendas_por_servico': [
            {'servico': servico, 'total': float(total)} 
            for servico, total in vendas_por_servico
        ],
        'vendas_por_dia': [
            {'dia': dia.strftime('%d/%m/%Y'), 'total': float(total)} 
            for dia, total in vendas_por_dia
        ],
        'total_vendas': float(total_vendas) if total_vendas else 0,
        'total_servicos': total_servicos
    })

@financeiro_bp.route('/vendas-recentes')
@login_required
def vendas_recentes():
    """
    Retorna as vendas mais recentes do barbeiro.
    """
    if not current_user.is_barbeiro():
        return jsonify({'status': 'error', 'message': 'Acesso negado'}), 403
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        return jsonify({'status': 'error', 'message': 'Perfil não encontrado'}), 404
    
    # Obter vendas recentes
    vendas = Venda.query.filter_by(barbeiro_id=perfil.id).order_by(Venda.created_at.desc()).limit(5).all()
    
    return jsonify({
        'vendas': [
            {
                'id': v.id,
                'data': v.data.strftime('%d/%m/%Y'),
                'hora': v.created_at.strftime('%H:%M'),
                'valor_total': float(v.valor_total),
                'forma_pagamento': v.forma_pagamento
            }
            for v in vendas
        ]
    })

@financeiro_bp.route('/detalhes-venda/<int:venda_id>')
@login_required
def detalhes_venda(venda_id):
    """
    Retorna os detalhes de uma venda específica.
    """
    if not current_user.is_barbeiro():
        return jsonify({'status': 'error', 'message': 'Acesso negado'}), 403
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        return jsonify({'status': 'error', 'message': 'Perfil não encontrado'}), 404
    
    venda = Venda.query.get_or_404(venda_id)
    
    # Verificar se a venda pertence ao barbeiro
    if venda.barbeiro_id != perfil.id:
        return jsonify({'status': 'error', 'message': 'Acesso negado a esta venda'}), 403
    
    # Obter itens da venda
    itens = ItemVenda.query.filter_by(venda_id=venda.id).all()
    itens_detalhes = []
    
    for item in itens:
        servico = Servico.query.get(item.servico_id)
        itens_detalhes.append({
            'servico': servico.nome,
            'quantidade': item.quantidade,
            'preco_unitario': float(item.preco_unitario),
            'desconto': float(item.desconto),
            'valor_total': float(item.valor_total)
        })
    
    return jsonify({
        'venda': {
            'id': venda.id,
            'data': venda.data.strftime('%d/%m/%Y'),
            'hora': venda.created_at.strftime('%H:%M'),
            'valor_total': float(venda.valor_total),
            'forma_pagamento': venda.forma_pagamento,
            'observacoes': venda.observacoes
        },
        'itens': itens_detalhes
    })
