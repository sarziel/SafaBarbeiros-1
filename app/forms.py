from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms import IntegerField, DecimalField, SelectMultipleField, TimeField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User
import phonenumbers
from datetime import datetime, time, date, timedelta

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar-me')

class RegistroClienteForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    telefone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=20)])
    password = PasswordField('Senha', validators=[
        DataRequired(), 
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        DataRequired(), 
        EqualTo('password', message='As senhas devem ser iguais')
    ])
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este e-mail já está em uso. Por favor, escolha outro.')
    
    def validate_telefone(self, telefone):
        try:
            input_number = phonenumbers.parse(telefone.data, "BR")
            if not phonenumbers.is_valid_number(input_number):
                raise ValidationError('Número de telefone inválido')
        except:
            raise ValidationError('Número de telefone inválido')

class RegistroBarbeiroForm(RegistroClienteForm):
    especialidade = StringField('Especialidade', validators=[Optional(), Length(max=100)])
    bio = TextAreaField('Sobre mim', validators=[Optional(), Length(max=500)])
    horario_inicio = TimeField('Horário de Início', validators=[DataRequired()], default=time(9, 0))
    horario_fim = TimeField('Horário de Término', validators=[DataRequired()], default=time(18, 0))
    
    def validate_horario_inicio(self, horario_inicio):
        if horario_inicio.data >= self.horario_fim.data:
            raise ValidationError('O horário de início deve ser anterior ao horário de término')

class PerfilBarbeiroForm(FlaskForm):
    telefone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=20)])
    especialidade = StringField('Especialidade', validators=[Optional(), Length(max=100)])
    bio = TextAreaField('Sobre mim', validators=[Optional(), Length(max=500)])
    horario_inicio = TimeField('Horário de Início', validators=[DataRequired()])
    horario_fim = TimeField('Horário de Término', validators=[DataRequired()])
    dias_trabalho = SelectMultipleField('Dias de Trabalho', 
                                      choices=[(1, 'Segunda'), (2, 'Terça'), (3, 'Quarta'), 
                                              (4, 'Quinta'), (5, 'Sexta'), (6, 'Sábado'), (7, 'Domingo')],
                                      coerce=int)
    duracao_padrao = IntegerField('Duração Padrão do Atendimento (minutos)', 
                                validators=[DataRequired()], default=30)
    
    def validate_telefone(self, telefone):
        try:
            input_number = phonenumbers.parse(telefone.data, "BR")
            if not phonenumbers.is_valid_number(input_number):
                raise ValidationError('Número de telefone inválido')
        except:
            raise ValidationError('Número de telefone inválido')
            
    def validate_horario_inicio(self, horario_inicio):
        if horario_inicio.data and self.horario_fim.data and horario_inicio.data >= self.horario_fim.data:
            raise ValidationError('O horário de início deve ser anterior ao horário de término')

class ServicoForm(FlaskForm):
    nome = StringField('Nome do Serviço', validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField('Descrição', validators=[Optional(), Length(max=200)])
    preco = DecimalField('Preço (R$)', validators=[DataRequired()], places=2)
    duracao = IntegerField('Duração (minutos)', validators=[DataRequired()], default=30)
    
    def validate_preco(self, preco):
        if preco.data <= 0:
            raise ValidationError('O preço deve ser maior que zero')
    
    def validate_duracao(self, duracao):
        if duracao.data <= 0:
            raise ValidationError('A duração deve ser maior que zero')

class AgendamentoForm(FlaskForm):
    barbeiro_id = SelectField('Barbeiro', coerce=int, validators=[DataRequired()])
    servico_id = SelectField('Serviço', coerce=int, validators=[DataRequired()])
    data = DateField('Data', validators=[DataRequired()], default=date.today)
    hora = TimeField('Horário', validators=[DataRequired()])
    observacoes = TextAreaField('Observações', validators=[Optional(), Length(max=200)])
    
    def validate_data(self, data):
        if data.data < date.today():
            raise ValidationError('A data não pode ser no passado')
        
        # Limitar agendamentos para no máximo 30 dias à frente
        if data.data > date.today() + timedelta(days=30):
            raise ValidationError('Agendamentos só podem ser feitos com até 30 dias de antecedência')
