"""
TESTE 2: Teste de Bloqueio de Acesso à Área Administrativa
Descrição: Testa as regras de autorização para áreas administrativas

Cenários testados:
- Usuário não autenticado tenta acessar admin → bloqueado
- Usuário comum tenta acessar admin → bloqueado
- Usuário admin acessa admin → permitido
- Acesso direto por URL sem permissão → bloqueado
"""

import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    """Cria uma instância de app para testes"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin
        admin = User(nome='Administrador', email='admin@teste.com', tipo='admin', ativo=True)
        admin.set_password('admin123')
        
        # Criar usuário comum
        user_comum = User(nome='Usuário Comum', email='comum@teste.com', tipo='comum', ativo=True)
        user_comum.set_password('senha123')
        
        db.session.add(admin)
        db.session.add(user_comum)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cria um cliente HTTP para testes"""
    return app.test_client()


class TestAdminAccess:
    """Testes de acesso à área administrativa"""
    
    def test_unauthenticated_user_cannot_access_admin(self, client):
        """
        Teste 2.1: Usuário não autenticado tenta acessar admin
        Resultado esperado: Redirecionar para login
        """
        response = client.get('/admin/', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()
    
    def test_common_user_cannot_access_admin_dashboard(self, client):
        """
        Teste 2.2: Usuário comum tenta acessar dashboard admin
        Resultado esperado: Acesso bloqueado
        """
        # Fazer login com usuário comum
        client.post('/auth/login', data={
            'email': 'comum@teste.com',
            'password': 'senha123'
        })
        
        # Tentar acessar admin
        response = client.get('/admin/', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'permissão' in response.data.lower() or b'não tem' in response.data.lower()
    
    def test_common_user_cannot_access_users_list(self, client):
        """Teste 2.3: Usuário comum tenta acessar lista de usuários"""
        client.post('/auth/login', data={
            'email': 'comum@teste.com',
            'password': 'senha123'
        })
        
        response = client.get('/admin/usuarios', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'permissão' in response.data.lower() or b'não tem' in response.data.lower()
    
    def test_admin_user_can_access_admin_dashboard(self, client):
        """
        Teste 2.4: Usuário admin acessa dashboard admin
        Resultado esperado: Acesso permitido
        """
        # Fazer login com admin
        client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'password': 'admin123'
        })
        
        # Acessar admin
        response = client.get('/admin/')
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Admin' in response.data
    
    def test_admin_user_can_access_users_list(self, client):
        """Teste 2.5: Usuário admin acessa lista de usuários"""
        client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'password': 'admin123'
        })
        
        response = client.get('/admin/usuarios')
        
        assert response.status_code == 200
    
    def test_direct_url_access_without_permission(self, client):
        """
        Teste 2.6: Acesso direto a rota administrativa sem permissão
        Resultado esperado: Bloqueado
        """
        # Tentar acessar sem estar logado
        response = client.get('/admin/usuarios/novo', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data.lower()
    
    def test_common_user_cannot_create_user(self, client):
        """Teste 2.7: Usuário comum tenta criar novo usuário"""
        # Fazer login com usuário comum
        client.post('/auth/login', data={
            'email': 'comum@teste.com',
            'password': 'senha123'
        })
        
        # Tentar acessar página de novo usuário
        response = client.get('/admin/usuarios/novo', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'permissão' in response.data.lower() or b'não tem' in response.data.lower()
    
    def test_admin_can_create_user(self, client):
        """Teste 2.8: Usuário admin consegue criar novo usuário"""
        # Fazer login com admin
        client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'password': 'admin123'
        })
        
        # Tentar acessar página de novo usuário
        response = client.get('/admin/usuarios/novo')
        
        assert response.status_code == 200
    
    def test_common_user_cannot_access_news_admin(self, client):
        """Teste 2.9: Usuário comum tenta acessar gerenciamento de notícias"""
        # Fazer login com usuário comum
        client.post('/auth/login', data={
            'email': 'comum@teste.com',
            'password': 'senha123'
        })
        
        # Tentar acessar admin de notícias
        response = client.get('/noticias/admin', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'permissão' in response.data.lower() or b'não tem' in response.data.lower()
    
    def test_admin_can_access_news_admin(self, client):
        """Teste 2.10: Usuário admin consegue acessar gerenciamento de notícias"""
        # Fazer login com admin
        client.post('/auth/login', data={
            'email': 'admin@teste.com',
            'password': 'admin123'
        })
        
        # Acessar admin de notícias
        response = client.get('/noticias/admin')
        
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
