from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, PerfilBarbeiro, Agendamento, Servico, Venda, ItemVenda
from app.forms import ServicoForm, PerfilBarbeiroForm
from datetime import datetime, timedelta
from sqlalchemy import and_, func

barbeiro_bp = Blueprint('barbeiro', __name__, url_prefix='/barbeiro')

@barbeiro_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Obter perfil do barbeiro
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        flash('Perfil de barbeiro não encontrado. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    # Obter data e hora atual
    now = datetime.now()
    hoje = now.date()
    hora_atual = now.time()
    
    # Obter agendamentos do dia
    agendamentos_hoje = Agendamento.query.filter(
        Agendamento.barbeiro_id == current_user.id,
        Agendamento.data == hoje,
        Agendamento.status != 'cancelado'
    ).order_by(Agendamento.hora_inicio).all()
    
    # Obter próximos agendamentos (7 dias)
    proxima_semana = hoje + timedelta(days=7)
    proximos_agendamentos = Agendamento.query.filter(
        Agendamento.barbeiro_id == current_user.id,
        Agendamento.data > hoje,
        Agendamento.data <= proxima_semana,
        Agendamento.status != 'cancelado'
    ).order_by(Agendamento.data, Agendamento.hora_inicio).all()
    
    # Gerar horários disponíveis em intervalos de 30 minutos (das 5h às 20h)
    horarios_disponiveis = {}
    
    # Início às 5h e término às 20h
    hora_inicio = time(5, 0)
    hora_fim = time(20, 0)
    
    # Lista de agendamentos hoje para verificar disponibilidade
    agendamentos_hoje_dict = {}
    for agendamento in agendamentos_hoje:
        inicio = agendamento.hora_inicio
        fim = agendamento.hora_fim
        
        # Marcar todos os horários de 30 min no intervalo do agendamento como ocupados
        current = datetime.combine(hoje, inicio)
        end = datetime.combine(hoje, fim)
        
        while current < end:
            slot = current.time().strftime('%H:%M')
            agendamentos_hoje_dict[slot] = agendamento
            current += timedelta(minutes=30)
    
    # Gerar todos os slots de 30 minutos entre hora_inicio e hora_fim
    current_time = datetime.combine(hoje, hora_inicio)
    end_time = datetime.combine(hoje, hora_fim)
    
    while current_time < end_time:
        slot = current_time.time().strftime('%H:%M')
        
        # Verificar se o horário já passou
        if current_time.time() < hora_atual:
            horarios_disponiveis[slot] = 'passado'
        # Verificar se o horário está ocupado
        elif slot in agendamentos_hoje_dict:
            horarios_disponiveis[slot] = 'ocupado'
        # Caso contrário, o horário está disponível
        else:
            horarios_disponiveis[slot] = 'disponivel'
            
        current_time += timedelta(minutes=30)
    
    # Obter estatísticas
    # Receita do dia
    receita_hoje = db.session.query(func.sum(Venda.valor_total)).\
        join(PerfilBarbeiro).\
        filter(
            PerfilBarbeiro.user_id == current_user.id,
            func.date(Venda.created_at) == hoje
        ).scalar() or 0
    
    # Receita da semana
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    receita_semana = db.session.query(func.sum(Venda.valor_total)).\
        join(PerfilBarbeiro).\
        filter(
            PerfilBarbeiro.user_id == current_user.id,
            func.date(Venda.created_at) >= inicio_semana,
            func.date(Venda.created_at) <= hoje
        ).scalar() or 0
    
    # Número de clientes atendidos hoje
    clientes_hoje = Venda.query.\
        join(PerfilBarbeiro).\
        filter(
            PerfilBarbeiro.user_id == current_user.id,
            func.date(Venda.created_at) == hoje
        ).count()
    
    return render_template('barbeiro/dashboard.html', 
                           perfil=perfil,
                           agendamentos_hoje=agendamentos_hoje,
                           proximos_agendamentos=proximos_agendamentos,
                           horarios_disponiveis=horarios_disponiveis,
                           receita_hoje=receita_hoje,
                           receita_semana=receita_semana,
                           clientes_hoje=clientes_hoje,
                           hoje=hoje,
                           title='Dashboard do Barbeiro')

@barbeiro_bp.route('/agenda')
@login_required
def agenda():
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    data = request.args.get('data', type=str)
    if data:
        try:
            data_selecionada = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            data_selecionada = datetime.now().date()
    else:
        data_selecionada = datetime.now().date()
    
    # Obter agendamentos da data selecionada
    agendamentos = Agendamento.query.filter(
        Agendamento.barbeiro_id == current_user.id,
        Agendamento.data == data_selecionada
    ).order_by(Agendamento.hora_inicio).all()
    
    return render_template('barbeiro/agenda.html', 
                           agendamentos=agendamentos,
                           data_selecionada=data_selecionada,
                           title='Agenda')

@barbeiro_bp.route('/marcar-concluido/<int:agendamento_id>', methods=['POST'])
@login_required
def marcar_concluido(agendamento_id):
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verificar se o agendamento pertence ao barbeiro
    if agendamento.barbeiro_id != current_user.id:
        flash('Acesso negado. Este agendamento não pertence a você.', 'danger')
        return redirect(url_for('barbeiro.agenda'))
    
    # Marcar como concluído
    agendamento.status = 'concluído'
    db.session.commit()
    
    flash('Agendamento marcado como concluído.', 'success')
    return redirect(url_for('barbeiro.agenda', data=agendamento.data.strftime('%Y-%m-%d')))

@barbeiro_bp.route('/servicos')
@login_required
def servicos():
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        flash('Perfil de barbeiro não encontrado. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    servicos = Servico.query.filter_by(barbeiro_id=perfil.id).all()
    
    return render_template('barbeiro/servicos.html',
                           servicos=servicos,
                           title='Meus Serviços')

@barbeiro_bp.route('/servicos/novo', methods=['GET', 'POST'])
@login_required
def novo_servico():
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        flash('Perfil de barbeiro não encontrado. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    form = ServicoForm()
    
    if form.validate_on_submit():
        servico = Servico(
            barbeiro_id=perfil.id,
            nome=form.nome.data,
            descricao=form.descricao.data,
            preco=form.preco.data,
            duracao=form.duracao.data,
            ativo=True
        )
        
        db.session.add(servico)
        db.session.commit()
        
        flash('Serviço adicionado com sucesso!', 'success')
        return redirect(url_for('barbeiro.servicos'))
    
    return render_template('barbeiro/editar_servico.html',
                           form=form,
                           title='Novo Serviço',
                           is_edit=False)

@barbeiro_bp.route('/servicos/editar/<int:servico_id>', methods=['GET', 'POST'])
@login_required
def editar_servico(servico_id):
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        flash('Perfil de barbeiro não encontrado. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    servico = Servico.query.get_or_404(servico_id)
    
    # Verificar se o serviço pertence ao barbeiro
    if servico.barbeiro_id != perfil.id:
        flash('Acesso negado. Este serviço não pertence a você.', 'danger')
        return redirect(url_for('barbeiro.servicos'))
    
    form = ServicoForm(obj=servico)
    
    if form.validate_on_submit():
        servico.nome = form.nome.data
        servico.descricao = form.descricao.data
        servico.preco = form.preco.data
        servico.duracao = form.duracao.data
        
        db.session.commit()
        
        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('barbeiro.servicos'))
    
    return render_template('barbeiro/editar_servico.html',
                           form=form,
                           servico=servico,
                           title='Editar Serviço',
                           is_edit=True)

@barbeiro_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        flash('Perfil de barbeiro não encontrado. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    form = PerfilBarbeiroForm(obj=perfil)
    
    if form.validate_on_submit():
        perfil.especialidade = form.especialidade.data
        perfil.bio = form.bio.data
        perfil.horario_inicio = form.horario_inicio.data
        perfil.horario_fim = form.horario_fim.data
        perfil.dias_trabalho = ','.join(map(str, form.dias_trabalho.data))
        perfil.duracao_padrao = form.duracao_padrao.data
        
        current_user.telefone = form.telefone.data
        
        db.session.commit()
        
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('barbeiro.dashboard'))
    
    # Preencher o formulário
    if request.method == 'GET':
        form.telefone.data = current_user.telefone
        if perfil.dias_trabalho:
            form.dias_trabalho.data = [int(dia) for dia in perfil.dias_trabalho.split(',')]
    
    return render_template('barbeiro/perfil.html',
                           form=form,
                           perfil=perfil,
                           title='Meu Perfil')

@barbeiro_bp.route('/pdv')
@login_required
def pdv():
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        flash('Perfil de barbeiro não encontrado. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    # Obter agendamentos do dia que ainda não foram pagos
    hoje = datetime.now().date()
    agendamentos = Agendamento.query.filter(
        Agendamento.barbeiro_id == current_user.id,
        Agendamento.data == hoje,
        Agendamento.status == 'concluído'
    ).outerjoin(Venda).filter(Venda.id == None).all()
    
    # Obter todos os serviços do barbeiro
    servicos = Servico.query.filter_by(barbeiro_id=perfil.id, ativo=True).all()
    
    return render_template('barbeiro/pdv.html',
                           agendamentos=agendamentos,
                           servicos=servicos,
                           title='PDV')

@barbeiro_bp.route('/registrar-venda', methods=['POST'])
@login_required
def registrar_venda():
    if not current_user.is_barbeiro():
        return jsonify({'status': 'error', 'message': 'Acesso negado'}), 403
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        return jsonify({'status': 'error', 'message': 'Perfil não encontrado'}), 404
    
    data = request.json
    itens = data.get('itens', [])
    
    if not itens:
        return jsonify({'status': 'error', 'message': 'Nenhum item na venda'}), 400
    
    # Calcular valor total
    valor_total = 0
    for item in itens:
        valor_total += item['quantidade'] * item['preco'] - item['desconto']
    
    # Criar venda
    venda = Venda(
        barbeiro_id=perfil.id,
        agendamento_id=data.get('agendamento_id'),
        data=datetime.now().date(),
        valor_total=valor_total,
        forma_pagamento=data.get('forma_pagamento'),
        observacoes=data.get('observacoes')
    )
    
    db.session.add(venda)
    db.session.flush()  # Para obter o ID da venda
    
    # Adicionar itens
    for item in itens:
        item_venda = ItemVenda(
            venda_id=venda.id,
            servico_id=item['servico_id'],
            quantidade=item['quantidade'],
            preco_unitario=item['preco'],
            desconto=item['desconto'],
            valor_total=(item['quantidade'] * item['preco']) - item['desconto']
        )
        db.session.add(item_venda)
    
    # Se for um agendamento, marcar como concluído
    if data.get('agendamento_id'):
        agendamento = Agendamento.query.get(data.get('agendamento_id'))
        if agendamento and agendamento.barbeiro_id == current_user.id:
            agendamento.status = 'concluído'
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Venda registrada com sucesso!', 'venda_id': venda.id})

@barbeiro_bp.route('/relatorios')
@login_required
def relatorios():
    if not current_user.is_barbeiro():
        flash('Acesso negado. Você não é um barbeiro.', 'danger')
        return redirect(url_for('auth.login'))
    
    perfil = PerfilBarbeiro.query.filter_by(user_id=current_user.id).first()
    if not perfil:
        flash('Perfil de barbeiro não encontrado. Entre em contato com o administrador.', 'warning')
        return redirect(url_for('auth.logout'))
    
    # Período
    periodo = request.args.get('periodo', 'semana')
    hoje = datetime.now().date()
    
    if periodo == 'dia':
        data_inicio = hoje
        data_fim = hoje
        titulo_periodo = 'Hoje'
    elif periodo == 'semana':
        data_inicio = hoje - timedelta(days=hoje.weekday())
        data_fim = hoje
        titulo_periodo = 'Esta Semana'
    elif periodo == 'mes':
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
        titulo_periodo = 'Este Mês'
    elif periodo == 'customizado':
        data_inicio_str = request.args.get('data_inicio')
        data_fim_str = request.args.get('data_fim')
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            titulo_periodo = f'{data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}'
        except (ValueError, TypeError):
            data_inicio = hoje - timedelta(days=hoje.weekday())
            data_fim = hoje
            titulo_periodo = 'Esta Semana'
    else:
        data_inicio = hoje - timedelta(days=hoje.weekday())
        data_fim = hoje
        titulo_periodo = 'Esta Semana'
    
    # Vendas no período
    vendas = Venda.query.filter(
        Venda.barbeiro_id == perfil.id,
        func.date(Venda.data) >= data_inicio,
        func.date(Venda.data) <= data_fim
    ).order_by(Venda.data.desc(), Venda.created_at.desc()).all()
    
    # Total de vendas
    total_vendas = sum(venda.valor_total for venda in vendas)
    
    # Contagem por forma de pagamento
    formas_pagamento = db.session.query(
        Venda.forma_pagamento, 
        func.sum(Venda.valor_total).label('total')
    ).filter(
        Venda.barbeiro_id == perfil.id,
        func.date(Venda.data) >= data_inicio,
        func.date(Venda.data) <= data_fim
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
        func.date(Venda.data) >= data_inicio,
        func.date(Venda.data) <= data_fim
    ).group_by(Servico.nome).all()
    
    # Dados para gráfico de vendas por dia
    vendas_por_dia = []
    if periodo != 'dia':
        vendas_por_dia = db.session.query(
            func.date(Venda.data).label('dia'),
            func.sum(Venda.valor_total).label('total')
        ).filter(
            Venda.barbeiro_id == perfil.id,
            func.date(Venda.data) >= data_inicio,
            func.date(Venda.data) <= data_fim
        ).group_by(func.date(Venda.data)).all()
    
    return render_template('barbeiro/relatorios.html',
                           vendas=vendas,
                           total_vendas=total_vendas,
                           formas_pagamento=formas_pagamento,
                           vendas_por_servico=vendas_por_servico,
                           vendas_por_dia=vendas_por_dia,
                           periodo=periodo,
                           titulo_periodo=titulo_periodo,
                           data_inicio=data_inicio,
                           data_fim=data_fim,
                           title='Relatórios Financeiros')
