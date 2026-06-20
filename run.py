from app import create_app
from app.routes import register_error_handlers

if __name__ == '__main__':
    app = create_app()
    register_error_handlers(app)
    
    # Executar servidor de desenvolvimento
    app.run(debug=True, host='0.0.0.0', port=5000)
