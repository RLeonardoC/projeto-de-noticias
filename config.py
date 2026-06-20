import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configurações gerais da aplicação"""
    
    # Secret key para sessões
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLite — não precisa de servidor de banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'news.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações de upload de arquivos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    JSON_SORT_KEYS = False
