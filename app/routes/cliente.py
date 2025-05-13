from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Agendamento, PerfilBarbeiro, Servico
from app.forms import AgendamentoForm
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')

@cliente_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_cliente():
        flash('Acesso negado. Você não é um cliente.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Obter agendamentos do cliente (futuros e recentes)
    hoje = datetime.now().date()
    agendamentos_futuros = Agendamento.query.filter(
        Agendamento.cliente_id == current_user.id,
        Agendamento.data >= hoje,
        Agendamento.status != 'cancelado'
    ).order_by(Agendamento.data, Agendamento.hora_inicio).limit(5).all()
    
    agendamentos_passados = Agendamento.query.filter(
        Agendamento.cliente_id == current_user.id,
        or_(Agendamento.data < hoje, 
            and_(Agendamento.data == hoje, Agendamento.status == 'concluído'))
    ).order_by(Agendamento.data.desc(), Agendamento.hora_inicio.desc()).limit(5).all()
    
    # Obter lista de barbeiros
    barbeiros = User.query.join(PerfilBarbeiro).filter(User.role == 2).all()
    
    return render_template('cliente/dashboard.html', 
                          agendamentos_futuros=agendamentos_futuros,
                          agendamentos_passados=agendamentos_passados,
                          barbeiros=barbeiros,
                          title='Dashboard do Cliente')

@cliente_bp.route('/agendamentos')
@login_required
def agendamentos():
    if not current_user.is_cliente():
        flash('Acesso negado. Você não é um cliente.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Obter todos os agendamentos do cliente
    agendamentos = Agendamento.query.filter(
        Agendamento.cliente_id == current_user.id
    ).order_by(Agendamento.data.desc(), Agendamento.hora_inicio.desc()).all()
    
    return render_template('cliente/agendamentos.html', 
                          agendamentos=agendamentos,
                          title='Meus Agendamentos')

@cliente_bp.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if not current_user.is_cliente():
        flash('Acesso negado. Você não é um cliente.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = AgendamentoForm()
    
    # Preencher as opções de barbeiros
    barbeiros = User.query.join(PerfilBarbeiro).filter(User.role == 2).all()
    form.barbeiro_id.choices = [(b.id, b.nome) for b in barbeiros]
    
    # Se o barbeiro foi selecionado, preencher os serviços disponíveis
    if request.method == 'GET' and request.args.get('barbeiro_id'):
        barbeiro_id = request.args.get('barbeiro_id', type=int)
        if barbeiro_id:
            barbeiro_perfil = PerfilBarbeiro.query.filter_by(user_id=barbeiro_id).first()
            if barbeiro_perfil:
                form.barbeiro_id.data = barbeiro_id
                servicos = Servico.query.filter_by(barbeiro_id=barbeiro_perfil.id, ativo=True).all()
                form.servico_id.choices = [(s.id, f"{s.nome} - R$ {s.preco:.2f}") for s in servicos]
    
    if form.validate_on_submit():
        barbeiro = User.query.get(form.barbeiro_id.data)
        servico = Servico.query.get(form.servico_id.data)
        
        if not barbeiro or not servico:
            flash('Barbeiro ou serviço inválido', 'danger')
            return redirect(url_for('cliente.agendar'))
        
        # Calcular horário de término
        hora_inicio = form.hora.data
        hora_fim = (datetime.combine(datetime.today(), hora_inicio) + 
                   timedelta(minutes=servico.duracao)).time()
        
        # Verificar se o horário está disponível
        horarios_ocupados = Agendamento.query.filter(
            Agendamento.barbeiro_id == barbeiro.id,
            Agendamento.data == form.data.data,
            Agendamento.status != 'cancelado',
            or_(
                and_(Agendamento.hora_inicio <= hora_inicio, Agendamento.hora_fim > hora_inicio),
                and_(Agendamento.hora_inicio < hora_fim, Agendamento.hora_fim >= hora_fim),
                and_(Agendamento.hora_inicio >= hora_inicio, Agendamento.hora_fim <= hora_fim)
            )
        ).all()
        
        if horarios_ocupados:
            flash('Horário indisponível. Por favor, escolha outro horário.', 'danger')
            return redirect(url_for('cliente.agendar'))
        
        # Criar agendamento
        agendamento = Agendamento(
            cliente_id=current_user.id,
            barbeiro_id=barbeiro.id,
            servico_id=servico.id,
            data=form.data.data,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            observacoes=form.observacoes.data,
            status='agendado'
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        flash('Agendamento realizado com sucesso!', 'success')
        return redirect(url_for('cliente.dashboard'))
    
    return render_template('cliente/novo_agendamento.html', 
                          form=form, 
                          title='Agendar Horário')

@cliente_bp.route('/cancelar/<int:agendamento_id>', methods=['POST'])
@login_required
def cancelar_agendamento(agendamento_id):
    if not current_user.is_cliente():
        flash('Acesso negado. Você não é um cliente.', 'danger')
        return redirect(url_for('auth.login'))
    
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verificar se o agendamento pertence ao cliente
    if agendamento.cliente_id != current_user.id:
        flash('Acesso negado. Este agendamento não pertence a você.', 'danger')
        return redirect(url_for('cliente.agendamentos'))
    
    # Verificar se o agendamento pode ser cancelado (24h antes)
    hoje = datetime.now()
    data_hora_agendamento = datetime.combine(agendamento.data, agendamento.hora_inicio)
    
    if (data_hora_agendamento - hoje).total_seconds() < 24 * 3600:
        flash('Não é possível cancelar agendamentos com menos de 24 horas de antecedência.', 'danger')
        return redirect(url_for('cliente.agendamentos'))
    
    # Cancelar agendamento
    agendamento.status = 'cancelado'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso.', 'success')
    return redirect(url_for('cliente.agendamentos'))
