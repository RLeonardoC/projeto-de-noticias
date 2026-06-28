"""
TESTE 1: Teste de Login
Descri coordção: Testa o fluxo completo de autenticação do sistema

Cenários testados:
- Login com credenciais válidas → sucesso
- Login com senha incorreta → erro
- Login com email inexistente → erro
- Login de usuário desativado → bloqueado
"""

import pytest
from app import create_app, db
from app.models import User
from flask_login import current_user


@pytest.fixture
def app():
    """Cria uma instância de app para testes"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        # Criar usuários de teste
        user_ativo = User(nome='Usuário Teste', email='usuario@teste.com', tipo='comum', ativo=True)
        user_ativo.set_password('senha123')
        
        user_desativado = User(nome='Usuário Desativado', email='desativado@teste.com', tipo='comum', ativo=False)
        user_desativado.set_password('senha456')
        
        db.session.add(user_ativo)
        db.session.add(user_desativado)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cria um cliente HTTP para testes"""
    return app.test_client()


class TestLogin:
    """Testes de login e autenticação"""
    
    def test_login_page_loads(self, client):
        """Testa se a página de login carrega corretamente"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_with_valid_credentials(self, client):
        """
        Teste 1.1: Login com credenciais válidas
        Resultado esperado: Usuário é logado e redirecionado para a página inicial
        """
        response = client.post('/auth/login', data={
            'email': 'usuario@teste.com',
            'password': 'senha123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Bem-vindo' in response.data
    
    def test_login_with_incorrect_password(self, client):
        """
        Teste 1.2: Login com senha incorreta
        Resultado esperado: Erro exibido, usuário não logado
        """
        response = client.post('/auth/login', data={
            'email': 'usuario@teste.com',
            'password': 'senha_errada'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'Senha incorreta' in response.data.decode()
    
    def test_login_with_nonexistent_email(self, client):
        """
        Teste 1.3: Login com email inexistente
        Resultado esperado: Erro exibido, usuário não logado
        """
        response = client.post('/auth/login', data={
            'email': 'naoexiste@teste.com',
            'password': 'qualquersenha'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'Email não encontrado' in response.data.decode()
    
    def test_login_with_inactive_user(self, client):
        """
        Teste 1.4: Login de usuário desativado
        Resultado esperado: Usuário é bloqueado de fazer login
        """
        response = client.post('/auth/login', data={
            'email': 'desativado@teste.com',
            'password': 'senha456'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'desativado' in response.data.decode() or 'Usuário desativado' in response.data.decode()
    
    def test_login_missing_email(self, client):
        """Testa login sem email"""
        response = client.post('/auth/login', data={
            'email': '',
            'password': 'senha123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'obrigatório' in response.data.decode().lower()
    
    def test_login_missing_password(self, client):
        """Testa login sem senha"""
        response = client.post('/auth/login', data={
            'email': 'usuario@teste.com',
            'password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'obrigatório' in response.data.decode().lower()
    
    def test_logout(self, client):
        """Testa logout do usuário"""
        # Fazer login primeiro
        client.post('/auth/login', data={
            'email': 'usuario@teste.com',
            'password': 'senha123'
        })
        
        # Fazer logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'desconectado' in response.data.lower()
    
    def test_authenticated_user_cannot_access_login_page(self, client):
        """Usuário autenticado é redirecionado ao tentar acessar login"""
        # Fazer login
        client.post('/auth/login', data={
            'email': 'usuario@teste.com',
            'password': 'senha123'
        })
        
        # Tentar acessar login novamente
        response = client.get('/auth/login', follow_redirects=True)
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
