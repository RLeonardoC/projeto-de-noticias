from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de Usuário"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), default='comum')  # 'admin' ou 'comum'
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Define a senha com hash seguro"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica se o usuário é admin"""
        return self.tipo == 'admin'
    
    def is_active(self):
        """Verifica se o usuário está ativo"""
        return self.ativo
    
    def __repr__(self):
        return f'<User {self.email}>'

class News(db.Model):
    """Modelo de Notícia"""
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    data_noticia = db.Column(db.Date, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    imagem = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<News {self.titulo}>'
