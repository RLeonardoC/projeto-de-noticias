#!/usr/bin/env python
from app import create_app, db
from app.models import User, News
from datetime import datetime

app = create_app()

with app.app_context():
    print("📊 Criando banco de dados...")
    db.create_all()
    
    admin = User.query.filter_by(email="admin@exemplo.com").first()
    
    if admin is None:
        print("👤 Criando usuários...")
        admin = User(
            nome="Administrador",
            email="admin@exemplo.com",
            tipo="admin",
            ativo=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        user_comum = User(
            nome="Usuário Teste",
            email="usuario@exemplo.com",
            tipo="comum",
            ativo=True
        )
        user_comum.set_password("usuario123")
        db.session.add(user_comum)
        
        db.session.commit()
        print("✅ Usuários criados!")
        
        print("📰 Criando notícia de teste...")
        noticia = News(
            titulo="Primeira Notícia",
            data_noticia=datetime.now().date(),
            texto="Esta é a primeira notícia do sistema para teste.",
            imagem=None,
            ativo=True,
            user_id=admin.id
        )
        db.session.add(noticia)
        db.session.commit()
        print("✅ Notícia criada!")
    else:
        print("ℹ️ Usuários já existem!")
    
    print("\n" + "="*50)
    print("🎉 BANCO DE DADOS PRONTO!")
    print("="*50)
    print("\n📝 Credenciais de teste:")
    print("   Email: admin@exemplo.com")
    print("   Senha: admin123")
    print("\n   Email (comum): usuario@exemplo.com")
    print("   Senha (comum): usuario123")
    print("\n🚀 Agora execute: python run.py")
    print("\n" + "="*50)