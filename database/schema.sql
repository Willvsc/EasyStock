-- ============================================
-- EasyStock
-- Estrutura do Banco de Dados
-- ============================================

PRAGMA foreign_keys = ON;


-- ============================================
-- TABELA: perfil
-- ============================================

CREATE TABLE IF NOT EXISTS perfil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT
);


-- ============================================
-- TABELA: usuario
-- ============================================

CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    perfil_id INTEGER NOT NULL,

    FOREIGN KEY (perfil_id)
        REFERENCES perfil(id)
);


-- ============================================
-- TABELA: categorias
-- ============================================

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);


-- ============================================
-- TABELA: produtos
-- ============================================

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 0,
    sku TEXT NOT NULL UNIQUE,
    categoria_id INTEGER NOT NULL,

    FOREIGN KEY (categoria_id)
        REFERENCES categorias(id)
);


-- ============================================
-- TABELA: movimentacoes
-- ============================================

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER,
    produto_nome TEXT,
    tipo TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    data_hora TEXT NOT NULL,

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON DELETE SET NULL
);


-- ============================================
-- PERFIS PADRÃO
-- ============================================

INSERT OR IGNORE INTO perfil (
    nome,
    descricao
)
VALUES
    (
        'Administrador',
        'Acesso completo ao sistema'
    ),
    (
        'Funcionário',
        'Acesso às operações de estoque'
    );


-- ============================================
-- CATEGORIAS PADRÃO
-- ============================================

INSERT OR IGNORE INTO categorias (nome)
VALUES
    ('Alimentos'),
    ('Bebidas'),
    ('Higiene'),
    ('Limpeza'),
    ('Mercearia'),
    ('Congelados'),
    ('Frutas e verduras'),
    ('Outros');