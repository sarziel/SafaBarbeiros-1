from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, PerfilBarbeiro, ROLE_CLIENTE, ROLE_BARBEIRO
from app.forms import LoginForm, RegistroClienteForm, RegistroBarbeiroForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_barbeiro():
            return redirect(url_for('barbeiro.dashboard'))
        else:
            return redirect(url_for('cliente.dashboard'))
            
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            if user.is_barbeiro():
                return redirect(next_page or url_for('barbeiro.dashboard'))
            else:
                return redirect(next_page or url_for('cliente.dashboard'))
        else:
            flash('E-mail ou senha incorretos', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/registro/cliente', methods=['GET', 'POST'])
def registro_cliente():
    if current_user.is_authenticated:
        return redirect(url_for('cliente.dashboard'))
        
    form = RegistroClienteForm()
    
    if form.validate_on_submit():
        user = User(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            role=ROLE_CLIENTE
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Registro de Cliente', 
                          user_type='cliente')

@auth_bp.route('/registro/barbeiro', methods=['GET', 'POST'])
def registro_barbeiro():
    if current_user.is_authenticated:
        return redirect(url_for('barbeiro.dashboard'))
        
    form = RegistroBarbeiroForm()
    
    if form.validate_on_submit():
        user = User(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            role=ROLE_BARBEIRO
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Criar perfil de barbeiro
        perfil = PerfilBarbeiro(
            user_id=user.id,
            especialidade=form.especialidade.data,
            bio=form.bio.data,
            horario_inicio=form.horario_inicio.data,
            horario_fim=form.horario_fim.data,
            dias_trabalho=','.join(map(str, form.dias_trabalho.data))
        )
        
        db.session.add(perfil)
        db.session.commit()
        
        flash('Conta de barbeiro criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Registro de Barbeiro', 
                          user_type='barbeiro')
