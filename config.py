import os
from urllib.parse import urlparse

class Config:
    # Configuração do banco de dados PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:BRIHfNrYSvhUDVayulkxWVMreiRJgCMJ@trolley.proxy.rlwy.net:57071/railway')
    
    # Configurações de segurança
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'safa-barbeiros-secret-key')
    
    # Configurações do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de upload (para fotos de perfil, se implementado)
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    
    # Configurações de e-mail (para notificações, se implementado)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Configurações para o Twilio (para SMS, se implementado)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
    # Configurações adicionais para produção
    # Sempre usar HTTPS em produção
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

# Escolher configuração com base no ambiente
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

# Configuração padrão
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
