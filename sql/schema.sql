-- Script de criação do banco de dados
-- Data: 21 de maio de 2026

CREATE DATABASE IF NOT EXISTS sistema_noticias;
USE sistema_noticias;

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'comum') DEFAULT 'comum',
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Notícias
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    data_noticia DATE NOT NULL,
    texto LONGTEXT NOT NULL,
    imagem VARCHAR(255),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserir usuário admin para testes
INSERT INTO users (nome, email, password_hash, tipo, ativo) 
VALUES ('Administrador', 'admin@exemplo.com', 'pbkdf2:sha256:600000$a1b2c3d4e5f6g7h8$1234567890abcdef1234567890abcdef12345678', 'admin', TRUE);

-- Inserir usuário comum para testes
INSERT INTO users (nome, email, password_hash, tipo, ativo) 
VALUES ('Usuário Teste', 'usuario@exemplo.com', 'pbkdf2:sha256:600000$a1b2c3d4e5f6g7h8$abcdef1234567890abcdef1234567890abcdef12', 'comum', TRUE);

-- Inserir notícia de exemplo
INSERT INTO news (titulo, data_noticia, texto, imagem, ativo) 
VALUES ('Primeira Notícia', '2026-05-21', 'Esta é a primeira notícia do sistema para teste.', 'noticia1.jpg', TRUE);

-- Índices para melhor performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_ativo ON users(ativo);
CREATE INDEX idx_news_ativo ON news(ativo);
CREATE INDEX idx_news_data ON news(data_noticia);
