from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Agendamento, Servico, Venda, PerfilBarbeiro
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator para verificar se o usuário é administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Dashboard do administrador"""
    # Contadores para estatísticas
    total_usuarios = User.query.count()
    total_barbeiros = User.query.filter_by(role=2).count()
    total_clientes = User.query.filter_by(role=1).count()
    total_agendamentos = Agendamento.query.count()
    
    # Últimos usuários registrados
    ultimos_usuarios = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Últimos agendamentos
    ultimos_agendamentos = Agendamento.query.order_by(Agendamento.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          title='Painel de Administração',
                          total_usuarios=total_usuarios,
                          total_barbeiros=total_barbeiros,
                          total_clientes=total_clientes,
                          total_agendamentos=total_agendamentos,
                          ultimos_usuarios=ultimos_usuarios,
                          ultimos_agendamentos=ultimos_agendamentos)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    """Lista de todos os usuários"""
    usuarios = User.query.all()
    return render_template('admin/usuarios.html', 
                          title='Gerenciar Usuários',
                          usuarios=usuarios)

@admin_bp.route('/barbeiros')
@login_required
@admin_required
def barbeiros():
    """Lista de todos os barbeiros"""
    barbeiros = User.query.filter_by(role=2).all()
    return render_template('admin/barbeiros.html', 
                          title='Gerenciar Barbeiros',
                          barbeiros=barbeiros)

@admin_bp.route('/relatorios')
@login_required
@admin_required
def relatorios():
    """Relatórios do sistema"""
    return render_template('admin/relatorios.html', 
                          title='Relatórios do Sistema')