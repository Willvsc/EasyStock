PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS perfil (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        );

CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            perfil_id INTEGER NOT NULL,

            FOREIGN KEY (perfil_id)
                REFERENCES perfil(id)
        );

CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        );

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

CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            produto_nome TEXT,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            usuario_id INTEGER,
            valor_unitario REAL,
            valor_total REAL,

            FOREIGN KEY (produto_id)
                REFERENCES produtos(id)
                ON DELETE SET NULL,

            FOREIGN KEY (usuario_id)
                REFERENCES usuario(id)
                ON DELETE SET NULL
        );

CREATE TABLE IF NOT EXISTS relatorios_arquivados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ano INTEGER NOT NULL,
            mes INTEGER NOT NULL,

            nome_arquivo TEXT NOT NULL,
            caminho_arquivo TEXT NOT NULL,

            tipo_geracao TEXT NOT NULL
                CHECK (
                    tipo_geracao IN (
                        'manual',
                        'automatico'
                    )
                ),

            data_geracao TEXT NOT NULL,

            usuario_id INTEGER,

            FOREIGN KEY (usuario_id)
                REFERENCES usuario(id)
                ON DELETE SET NULL,

            UNIQUE (ano, mes)
        );

CREATE INDEX IF NOT EXISTS idx_mov_data ON movimentacoes(data_hora);

CREATE INDEX IF NOT EXISTS idx_mov_produto ON movimentacoes(produto_id);

CREATE INDEX IF NOT EXISTS idx_prod_categoria ON produtos(categoria_id);
INSERT OR IGNORE INTO perfil(nome,descricao) VALUES ('Administrador','Acesso completo'),('Gerente','Gestão de estoque'),('Funcionário','Operações de estoque');
INSERT OR IGNORE INTO categorias(nome) VALUES ('Alimentos'),('Bebidas'),('Higiene'),('Limpeza'),('Mercearia'),('Congelados'),('Frutas e verduras'),('Outros');
