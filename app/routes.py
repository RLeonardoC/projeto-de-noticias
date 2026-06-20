from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, News
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from functools import wraps

# ============== BLUEPRINTS ==============

# Blueprint de Autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Blueprint de Administração
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Blueprint de Notícias
news_bp = Blueprint('news', __name__, url_prefix='/noticias')

# Blueprint Principal
main_bp = Blueprint('main', __name__)

# ============== DECORADORES ==============

def admin_required(f):
    """Decorador para verificar se o usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa estar logado.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Você não tem permissão para acessar esta área.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    from config import Config
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ============== ROTAS DE AUTENTICAÇÃO ==============

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validações
        if not email or not password:
            flash('Email e senha são obrigatórios.', 'error')
            return redirect(url_for('auth.login'))
        
        # Buscar usuário
        user = User.query.filter_by(email=email).first()
        
        # Teste 1: Login com credenciais válidas / inválidas / usuário desativado
        if user is None:
            flash('Email não encontrado.', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.check_password(password):
            flash('Senha incorreta.', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.ativo:
            flash('Usuário desativado. Entre em contato com o administrador.', 'error')
            return redirect(url_for('auth.login'))
        
        # Login bem-sucedido
        login_user(user)
        flash(f'Bem-vindo, {user.nome}!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Rota de logout"""
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('main.index'))

# ============== ROTAS DE ADMINISTRAÇÃO ==============

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Página inicial de admin - listar usuários"""
    users = User.query.all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    """Listar usuários"""
    users = User.query.all()
    return render_template('admin/usuarios.html', users=users)

@admin_bp.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_usuario():
    """Criar novo usuário"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        tipo = request.form.get('tipo', 'comum')
        
        # Validações
        if not nome or not email or not password:
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('admin.novo_usuario'))
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('admin.novo_usuario'))
        
        if tipo not in ['admin', 'comum']:
            flash('Tipo de usuário inválido.', 'error')
            return redirect(url_for('admin.novo_usuario'))
        
        # Criar usuário
        user = User(nome=nome, email=email, tipo=tipo)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Usuário {nome} criado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/novo_usuario.html')

@admin_bp.route('/usuarios/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(user_id):
    """Editar usuário"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.nome = request.form.get('nome', '').strip()
        user.email = request.form.get('email', '').strip()
        user.tipo = request.form.get('tipo', 'comum')
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/editar_usuario.html', user=user)

@admin_bp.route('/usuarios/<int:user_id>/desativar', methods=['POST'])
@login_required
@admin_required
def desativar_usuario(user_id):
    """Desativar usuário"""
    user = User.query.get_or_404(user_id)
    user.ativo = False
    db.session.commit()
    flash(f'Usuário {user.nome} desativado.', 'success')
    return redirect(url_for('admin.usuarios'))

# ============== ROTAS DE NOTÍCIAS ==============

@news_bp.route('/')
def listar_noticias():
    """Listar todas as notícias ativas na página pública"""
    noticias = News.query.filter_by(ativo=True).order_by(News.data_noticia.desc()).all()
    return render_template('news/listar.html', noticias=noticias)

@news_bp.route('/<int:noticia_id>')
def detalhes_noticia(noticia_id):
    """Detalhes de uma notícia"""
    noticia = News.query.get_or_404(noticia_id)
    if not noticia.ativo:
        flash('Notícia não encontrada.', 'error')
        return redirect(url_for('news.listar_noticias'))
    return render_template('news/detalhes.html', noticia=noticia)

@news_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def nova_noticia():
    """Criar nova notícia (apenas admin)"""
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        data_noticia = request.form.get('data_noticia')
        texto = request.form.get('texto', '').strip()
        imagem = None
        
        # Validações
        if not titulo or not data_noticia or not texto:
            flash('Título, data e texto são obrigatórios.', 'error')
            return redirect(url_for('news.nova_noticia'))
        
        # Processar upload de imagem
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S_')
                filename = timestamp + filename
                
                # Garantir que a pasta existe
                os.makedirs('app/static/images', exist_ok=True)
                file.save(os.path.join('app/static/images', filename))
                imagem = filename
        
        # Criar notícia
        noticia = News(
            titulo=titulo,
            data_noticia=datetime.strptime(data_noticia, '%Y-%m-%d').date(),
            texto=texto,
            imagem=imagem
        )
        
        db.session.add(noticia)
        db.session.commit()
        
        flash('Notícia criada com sucesso!', 'success')
        return redirect(url_for('news.listar_noticias_admin'))
    
    return render_template('news/nova_noticia.html')

@news_bp.route('/admin')
@login_required
@admin_required
def listar_noticias_admin():
    """Listar todas as notícias para admin (inclusive desativadas)"""
    noticias = News.query.order_by(News.data_noticia.desc()).all()
    return render_template('news/admin_list.html', noticias=noticias)

@news_bp.route('/<int:noticia_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_noticia(noticia_id):
    """Editar notícia"""
    noticia = News.query.get_or_404(noticia_id)
    
    if request.method == 'POST':
        noticia.titulo = request.form.get('titulo', '').strip()
        noticia.data_noticia = datetime.strptime(request.form.get('data_noticia'), '%Y-%m-%d').date()
        noticia.texto = request.form.get('texto', '').strip()
        
        # Processar upload de imagem
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                # Deletar imagem antiga se existir
                if noticia.imagem and os.path.exists(f'app/static/images/{noticia.imagem}'):
                    os.remove(f'app/static/images/{noticia.imagem}')
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S_')
                filename = timestamp + filename
                
                os.makedirs('app/static/images', exist_ok=True)
                file.save(os.path.join('app/static/images', filename))
                noticia.imagem = filename
        
        db.session.commit()
        flash('Notícia atualizada com sucesso!', 'success')
        return redirect(url_for('news.listar_noticias_admin'))
    
    return render_template('news/editar_noticia.html', noticia=noticia)

@news_bp.route('/<int:noticia_id>/desativar', methods=['POST'])
@login_required
@admin_required
def desativar_noticia(noticia_id):
    """Desativar notícia (soft delete)"""
    noticia = News.query.get_or_404(noticia_id)
    noticia.ativo = False
    db.session.commit()
    flash('Notícia desativada com sucesso!', 'success')
    return redirect(url_for('news.listar_noticias_admin'))

@news_bp.route('/<int:noticia_id>/ativar', methods=['POST'])
@login_required
@admin_required
def ativar_noticia(noticia_id):
    """Ativar notícia"""
    noticia = News.query.get_or_404(noticia_id)
    noticia.ativo = True
    db.session.commit()
    flash('Notícia ativada com sucesso!', 'success')
    return redirect(url_for('news.listar_noticias_admin'))

# ============== ROTAS PRINCIPAIS ==============

@main_bp.route('/')
def index():
    """Página inicial pública"""
    noticias_destaque = News.query.filter_by(ativo=True).order_by(News.data_noticia.desc()).limit(5).all()
    return render_template('index.html', noticias_destaque=noticias_destaque)

@main_bp.route('/sobre')
def sobre():
    """Página sobre"""
    return render_template('sobre.html')

# ============== TRATAMENTO DE ERROS ==============

def register_error_handlers(app):
    """Registrar handlers de erro"""
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
