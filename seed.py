"""
Script para criar as tabelas e o usuário admin inicial.
Execute uma única vez:  python seed.py
"""
from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    db.create_all()
    print("✔ Tabelas criadas.")

    # Admin exigido pelo professor (admin@exemplo.com / admin123)
    if not User.query.filter_by(email='admin@exemplo.com').first():
        admin = User(nome='Administrador', email='admin@exemplo.com', tipo='admin', ativo=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✔ Admin criado → admin@exemplo.com / admin123")
    else:
        print("ℹ Admin já existe.")
