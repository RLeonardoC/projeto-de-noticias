from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, User

def create_app(config_class=Config):
    """Factory function para criar a aplicação Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Criar contexto de aplicação para criar tabelas
    with app.app_context():
        db.create_all()
    
    # Registrar blueprints
    from app.routes import auth_bp, admin_bp, news_bp, main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(main_bp)
    
    return app
