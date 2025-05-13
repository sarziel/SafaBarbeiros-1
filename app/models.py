from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# User role constants
ROLE_CLIENTE = 1
ROLE_BARBEIRO = 2
ROLE_ADMIN = 3

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Integer, nullable=False)  # 1 = Cliente, 2 = Barbeiro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    perfil_barbeiro = db.relationship('PerfilBarbeiro', backref='user', uselist=False, lazy=True)
    agendamentos_cliente = db.relationship('Agendamento', backref='cliente', 
                                         foreign_keys='Agendamento.cliente_id', lazy=True)
    agendamentos_barbeiro = db.relationship('Agendamento', backref='barbeiro', 
                                          foreign_keys='Agendamento.barbeiro_id', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_barbeiro(self):
        return self.role == ROLE_BARBEIRO
    
    def is_cliente(self):
        return self.role == ROLE_CLIENTE
        
    def is_admin(self):
        return self.role == ROLE_ADMIN

class PerfilBarbeiro(db.Model):
    __tablename__ = 'perfis_barbeiro'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    especialidade = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    horario_inicio = db.Column(db.Time, nullable=False, default=datetime.strptime('09:00', '%H:%M').time())
    horario_fim = db.Column(db.Time, nullable=False, default=datetime.strptime('18:00', '%H:%M').time())
    dias_trabalho = db.Column(db.String(20), nullable=False, default='1,2,3,4,5')  # dias da semana (1-7)
    duracao_padrao = db.Column(db.Integer, nullable=False, default=30)  # minutos
    foto_url = db.Column(db.String(255), nullable=True)
    
    # Relacionamentos
    servicos = db.relationship('Servico', backref='barbeiro', lazy=True)

class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('perfis_barbeiro.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    duracao = db.Column(db.Integer, nullable=False)  # duração em minutos
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    itens_venda = db.relationship('ItemVenda', backref='servico', lazy=True)

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='agendado')  # agendado, concluído, cancelado
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    servico = db.relationship('Servico', backref='agendamentos')
    venda = db.relationship('Venda', backref='agendamento', uselist=False, lazy=True)

class Venda(db.Model):
    __tablename__ = 'vendas'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('perfis_barbeiro.id'), nullable=False)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=True)
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)  # dinheiro, cartão_credito, cartão_debito, pix
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    itens = db.relationship('ItemVenda', backref='venda', lazy=True)
    barbeiro = db.relationship('PerfilBarbeiro', backref='vendas')

class ItemVenda(db.Model):
    __tablename__ = 'itens_venda'
    
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    desconto = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
