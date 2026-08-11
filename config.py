"""
Configurações da aplicação Flask
"""
import os
from datetime import timedelta

class Config:
    """Configurações base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') # Lembrem de mudar esta mer...
    SQLALCHEMY_DATABASE_URI = 'sqlite:///inventory.db' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Configurações de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Seleciona configuração baseado no ambiente
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(name=None):
    """Retorna a configuração apropriada"""
    if name is None:
        name = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(name, DevelopmentConfig)
