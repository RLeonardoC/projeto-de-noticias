"""
conftest.py - Configurações compartilhadas para testes
"""

import pytest
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db
from app.models import User, News
from datetime import datetime


@pytest.fixture(scope="function")
def test_app():
    """Cria uma aplicação Flask para testes"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def test_client(test_app):
    """Cria um cliente HTTP para testes"""
    return test_app.test_client()


@pytest.fixture(scope="function")
def test_db(test_app):
    """Retorna a instância do banco de dados"""
    with test_app.app_context():
        yield db


@pytest.fixture(scope="function")
def create_test_users(test_app):
    """Cria usuários de teste padrão"""
    with test_app.app_context():
        admin = User(
            nome='Admin Teste',
            email='admin@teste.com',
            tipo='admin',
            ativo=True
        )
        admin.set_password('admin123')
        
        user_comum = User(
            nome='Usuário Comum',
            email='usuario@teste.com',
            tipo='comum',
            ativo=True
        )
        user_comum.set_password('senha123')
        
        user_desativado = User(
            nome='Usuário Desativado',
            email='desativado@teste.com',
            tipo='comum',
            ativo=False
        )
        user_desativado.set_password('senha456')
        
        db.session.add_all([admin, user_comum, user_desativado])
        db.session.commit()
        
        return {
            'admin': admin,
            'comum': user_comum,
            'desativado': user_desativado
        }


@pytest.fixture(scope="function")
def create_test_news(test_app):
    """Cria notícias de teste"""
    with test_app.app_context():
        noticia1 = News(
            titulo='Notícia 1',
            data_noticia=datetime.now().date(),
            texto='Texto da notícia 1',
            imagem=None,
            ativo=True
        )
        
        noticia2 = News(
            titulo='Notícia 2',
            data_noticia=datetime.now().date(),
            texto='Texto da notícia 2',
            imagem=None,
            ativo=True
        )
        
        noticia_desativada = News(
            titulo='Notícia Desativada',
            data_noticia=datetime.now().date(),
            texto='Texto da notícia desativada',
            imagem=None,
            ativo=False
        )
        
        db.session.add_all([noticia1, noticia2, noticia_desativada])
        db.session.commit()
        
        return {
            'ativa1': noticia1,
            'ativa2': noticia2,
            'desativada': noticia_desativada
        }
