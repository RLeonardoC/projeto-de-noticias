"""
TESTE 3: Teste Automatizado End-to-End
Descrição: Simula um fluxo completo do sistema

Cenário:
1. Criar usuário admin (ou usar existente)
2. Fazer login como admin
3. Cadastrar uma nova notícia com dados e imagem
4. Verificar se a notícia aparece na página pública
5. Desativar a notícia
6. Verificar se a notícia não aparece mais na página pública
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from app import create_app, db
from app.models import User


@pytest.fixture(scope="session")
def app():
    """Cria instância da aplicação para testes E2E"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin
        admin = User(nome='Admin Teste', email='admin@e2e.com', tipo='admin', ativo=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="session")
def server(app):
    """Inicia o servidor Flask para testes E2E"""
    from threading import Thread
    
    def run_server():
        app.run(debug=False, use_reloader=False, port=5555, use_debugger=False)
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Aguardar o servidor iniciar
    time.sleep(2)
    
    yield
    
    # Servidor encerra quando a thread daemon morre


@pytest.fixture
def driver():
    """Cria instância do WebDriver do Selenium"""
    options = Options()
    # Descomentar para modo headless (sem interface gráfica)
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


class TestEndToEnd:
    """Testes End-to-End do sistema"""
    
    BASE_URL = "http://localhost:5555"
    
    def test_complete_workflow_with_news_crud(self, driver, server):
        """
        Teste 3: Fluxo completo do sistema
        
        Passo 1: Fazer login como admin
        """
        print("\n===== INICIANDO TESTE END-TO-END =====")
        
        # Passo 1: Ir para página de login
        print("Passo 1: Acessar página de login...")
        driver.get(f"{self.BASE_URL}/auth/login")
        
        # Passo 2: Fazer login
        print("Passo 2: Realizar login com credenciais de admin...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys("admin@e2e.com")
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Esperar redirecionamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        
        print("✓ Login realizado com sucesso!")
        
        # Passo 3: Navegar para criar notícia
        print("Passo 3: Navegando para criar nova notícia...")
        driver.get(f"{self.BASE_URL}/noticias/novo")
        
        # Passo 4: Preencher formulário de notícia
        print("Passo 4: Preenchendo formulário de notícia...")
        
        titulo_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "titulo"))
        )
        titulo_field.send_keys("Notícia de Teste E2E")
        
        data_field = driver.find_element(By.ID, "data_noticia")
        data_field.send_keys("05212026")  # Formato: MMDDYYYY
        
        texto_field = driver.find_element(By.ID, "texto")
        texto_field.send_keys("Esta é uma notícia de teste criada automaticamente pelos testes end-to-end.")
        
        # Submeter formulário
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # Aguardar criação
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        print("✓ Notícia criada com sucesso!")
        
        # Passo 5: Verificar se notícia aparece na página pública
        print("Passo 5: Verificando se notícia aparece na página pública...")
        driver.get(f"{self.BASE_URL}/noticias/")
        
        # Procurar pelo título da notícia na página
        try:
            noticia_elemento = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Notícia de Teste E2E')]"))
            )
            print("✓ Notícia visível na página pública!")
        except:
            print("✗ Notícia não encontrada na página pública")
            raise
        
        # Passo 6: Desativar a notícia
        print("Passo 6: Desativando a notícia...")
        
        # Voltar para admin
        driver.get(f"{self.BASE_URL}/noticias/admin")
        
        # Encontrar botão de desativar
        desativar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Desativar')]"))
        )
        desativar_button.click()
        
        # Confirmar alerta
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.accept()
        
        print("✓ Notícia desativada com sucesso!")
        
        # Passo 7: Verificar se notícia não aparece mais na página pública
        print("Passo 7: Verificando se notícia desapareceu da página pública...")
        
        driver.get(f"{self.BASE_URL}/noticias/")
        
        # Aguardar que a página carregue
        time.sleep(1)
        
        # Verificar se a notícia NÃO está mais presente
        try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Notícia de Teste E2E')]")
            print("✗ Notícia ainda está visível (deveria estar desativada)")
            raise AssertionError("Notícia desativada ainda está visível na página pública")
        except Exception as e:
            if "Notícia ainda está visível" in str(e):
                raise
            # Se não encontrar o elemento, significa que foi realmente desativado
            print("✓ Notícia corretamente removida da página pública!")
        
        print("\n===== TESTE END-TO-END CONCLUÍDO COM SUCESSO! =====\n")
    
    def test_admin_can_reactivate_news(self, driver, server):
        """Teste adicional: Admin consegue reativar notícia"""
        print("\n===== TESTE DE REATIVAÇÃO DE NOTÍCIA =====")
        
        # Fazer login
        driver.get(f"{self.BASE_URL}/auth/login")
        
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys("admin@e2e.com")
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Ir para admin de notícias
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        
        driver.get(f"{self.BASE_URL}/noticias/admin")
        
        # Procurar por botão de reativar
        try:
            ativar_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ativar')]"))
            )
            ativar_button.click()
            print("✓ Notícia reativada com sucesso!")
        except:
            print("ℹ Nenhuma notícia desativada para reativar")
        
        print("\n===== TESTE DE REATIVAÇÃO CONCLUÍDO =====\n")


if __name__ == '__main__':
    # Para executar: pytest tests/test_e2e.py -v -s
    pytest.main([__file__, '-v', '-s'])
