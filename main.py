from flask import Flask, jsonify, request, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "easystock-chave-local-desenvolvimento"
)

DATABASE = "estoque.db"

# ==============================
# CONEXÃO COM O BANCO
# ============================== 

def conectar_banco():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==============================
# INICIALIZAÇÃO DO BANCO
# ==============================

def inicializar_banco():

    conn = conectar_banco()


    # ==============================
    # TABELA DE PERFIS
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS perfil (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
    """)


    # ==============================
    # TABELA DE USUÁRIOS
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            perfil_id INTEGER NOT NULL,
            FOREIGN KEY (perfil_id) REFERENCES perfil(id)
        )
    """)


    # ==============================
    # TABELA DE CATEGORIAS
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)


    # ==============================
    # TABELA DE PRODUTOS
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0,
            sku TEXT NOT NULL UNIQUE,
            categoria_id INTEGER NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)


    # ==============================
    # TABELA DE MOVIMENTAÇÕES
    # ==============================

    conn.execute("""
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
    )
""")

    # ==============================
    # PERFIS PADRÃO
    # ==============================

    perfis_padrao = [
        (
            "Administrador",
            "Acesso completo ao sistema"
        ),
        (
            "Funcionário",
            "Acesso às operações de estoque"
        )
    ]

    for nome, descricao in perfis_padrao:

        conn.execute("""
            INSERT OR IGNORE INTO perfil (
                nome,
                descricao
            )
            VALUES (?, ?)
        """, (
            nome,
            descricao
        ))


    # ==============================
    # CATEGORIAS PADRÃO
    # ==============================

    categorias_padrao = [
        "Alimentos",
        "Bebidas",
        "Higiene",
        "Limpeza",
        "Mercearia",
        "Congelados",
        "Frutas e verduras",
        "Outros"
    ]

    for categoria in categorias_padrao:

        conn.execute("""
            INSERT OR IGNORE INTO categorias (nome)
            VALUES (?)
        """, (categoria,))

    # ==============================
    # ADMINISTRADOR INICIAL
    # ==============================

    perfil_admin = conn.execute("""
        SELECT id
        FROM perfil
        WHERE nome = ?
    """, ("Administrador",)).fetchone()

    administrador = conn.execute("""
        SELECT id
        FROM usuario
        WHERE email = ?
    """, ("admin@easystock.com",)).fetchone()

    if perfil_admin and not administrador:

        senha_admin = generate_password_hash(
            "Admin123"
        )

        conn.execute("""
            INSERT INTO usuario (
                nome,
                email,
                senha,
                perfil_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            "Administrador",
            "admin@easystock.com",
            senha_admin,
            perfil_admin["id"]
        ))
    conn.commit()
    conn.close()

# ==============================
# PÁGINA PRINCIPAL
# ==============================

@app.route("/")
def pagina_inicial():

    if "usuario_id" not in session:
        return redirect("/login")

    return render_template("index.html")


# ==============================
# LISTAR PRODUTOS
# ==============================

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():

    conn = conectar_banco()

    produtos = conn.execute("""
        SELECT
            produtos.id,
            produtos.nome,
            produtos.preco,
            produtos.quantidade,
            produtos.sku,
            produtos.categoria_id,
            categorias.nome AS categoria
        FROM produtos
        LEFT JOIN categorias
            ON produtos.categoria_id = categorias.id
        ORDER BY produtos.nome ASC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(produto)
        for produto in produtos
    ])

# ==============================
# LISTAR CATEGORIAS
# ==============================

@app.route("/api/categorias", methods=["GET"])
def listar_categorias():

    conn = conectar_banco()

    categorias = conn.execute("""
        SELECT id, nome
        FROM categorias
        ORDER BY nome ASC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(categoria)
        for categoria in categorias
    ])


# ==============================
# CADASTRAR PRODUTO
# ==============================

@app.route("/api/produtos", methods=["POST"])
def adicionar_produto():

    dados = request.get_json()

    nome = dados.get("nome", "").strip()
    categoria = dados.get("categoria", "").strip()
    preco = dados.get("preco")
    quantidade = dados.get("quantidade")
    sku = dados.get("sku", "").strip()

    # Validação dos campos de texto

    if not nome or not categoria or not sku:

        return jsonify({
            "erro": "Preencha todos os campos obrigatórios."
        }), 400

    if len(nome) > 100:

        return jsonify({
        "erro": "O nome do produto deve ter no máximo 100 caracteres."
    }), 400


    if len(sku) > 30:

        return jsonify({
        "erro": "O SKU deve ter no máximo 30 caracteres."
    }), 400

    # Conversão dos valores numéricos

    try:

        preco = float(preco)
        quantidade = int(quantidade)

    except (ValueError, TypeError):

        return jsonify({
            "erro": "Preço ou quantidade inválidos."
        }), 400


    # Impedir valores negativos

   
    if preco <= 0:

        return jsonify({
        "erro": "O preço deve ser maior que zero."
    }), 400


    if quantidade < 0:

        return jsonify({
        "erro": "A quantidade não pode ser negativa."
    }), 400

    # Localizar a categoria selecionada

    categoria_banco = conn.execute("""
        SELECT id
        FROM categorias
        WHERE nome = ?
    """, (categoria,)).fetchone()


    if not categoria_banco:

        conn.close()

        return jsonify({
            "erro": "Categoria não encontrada."
        }), 400


    categoria_id = categoria_banco["id"]


    try:

        conn.execute("""
            INSERT INTO produtos
            (
                nome,
                categoria_id,
                preco,
                quantidade,
                sku
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            nome,
            categoria_id,
            preco,
            quantidade,
            sku
        ))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "erro": "Já existe um produto com esse SKU."
        }), 400


    conn.close()

    return jsonify({
        "mensagem": "Produto cadastrado com sucesso!"
    }), 201

# ==============================
# EDITAR PRODUTO
# ==============================

@app.route("/api/produtos/<int:produto_id>", methods=["PUT"])
def editar_produto(produto_id):

    dados = request.get_json()

    nome = dados.get("nome", "").strip()
    categoria = dados.get("categoria", "").strip()
    preco = dados.get("preco")
    sku = dados.get("sku", "").strip()


    # Validar campos obrigatórios

    if not nome or not categoria or not sku:

        return jsonify({
            "erro": "Preencha todos os campos obrigatórios."
        }), 400

    if len(nome) > 100:

        return jsonify({
        "erro": "O nome do produto deve ter no máximo 100 caracteres."
    }), 400


    if len(sku) > 30:

        return jsonify({
        "erro": "O SKU deve ter no máximo 30 caracteres."
    }), 400

    # Converter preço

    try:

        preco = float(preco)

    except (ValueError, TypeError):

        return jsonify({
            "erro": "Preço inválido."
        }), 400


    # Impedir preço negativo

    if preco <= 0:

        return jsonify({
        "erro": "O preço deve ser maior que zero."
    }), 400


    conn = conectar_banco()

    # Localizar a categoria selecionada

    categoria_banco = conn.execute("""
        SELECT id
        FROM categorias
        WHERE nome = ?
    """, (categoria,)).fetchone()


    if not categoria_banco:

        conn.close()

        return jsonify({
            "erro": "Categoria não encontrada."
        }), 400


    categoria_id = categoria_banco["id"]
    # Verificar se o produto existe

    produto = conn.execute("""
        SELECT *
        FROM produtos
        WHERE id = ?
    """, (produto_id,)).fetchone()


    if not produto:

        conn.close()

        return jsonify({
            "erro": "Produto não encontrado."
        }), 404


    # Verificar se o novo SKU já pertence
    # a outro produto

    outro_produto = conn.execute("""
        SELECT *
        FROM produtos
        WHERE sku = ?
        AND id != ?
    """, (
        sku,
        produto_id
    )).fetchone()


    if outro_produto:

        conn.close()

        return jsonify({
            "erro": "Esse SKU já está sendo usado por outro produto."
        }), 400


    # Atualizar produto 

    conn.execute("""
        UPDATE produtos
        SET
            nome = ?,
            categoria_id = ?,
            preco = ?,
            sku = ?
        WHERE id = ?
    """, (
        nome,
        categoria_id,
        preco,
        sku,
        produto_id
    ))


    conn.commit()
    conn.close()


    return jsonify({
        "mensagem": "Produto atualizado com sucesso!"
    })


# ==============================
# ALTERAR QUANTIDADE
# ==============================

@app.route(
    "/api/produtos/<int:produto_id>/quantidade",
    methods=["PATCH"]
)
def alterar_quantidade(produto_id):

    dados = request.get_json()

    operacao = dados.get("operacao")


    if operacao not in ["adicionar", "remover"]:

        return jsonify({
            "erro": "Operação inválida."
        }), 400


    conn = conectar_banco()


    produto = conn.execute("""
        SELECT *
        FROM produtos
        WHERE id = ?
    """, (produto_id,)).fetchone()


    if not produto:

        conn.close()

        return jsonify({
            "erro": "Produto não encontrado."
        }), 404


    quantidade_atual = produto["quantidade"]


    if operacao == "adicionar":

        nova_quantidade = quantidade_atual + 1
        tipo_movimentacao = "entrada"

    else:

        if quantidade_atual <= 0:

            conn.close()

        return jsonify({
            "erro": "Não é possível realizar a saída. O produto está sem estoque."
        }), 400

    nova_quantidade = quantidade_atual - 1

    tipo_movimentacao = "saida"


    # ==============================
    # ATUALIZAR ESTOQUE
    # ==============================

    conn.execute("""
        UPDATE produtos
        SET quantidade = ?
        WHERE id = ?
    """, (
        nova_quantidade,
        produto_id
    ))


    # ==============================
    # REGISTRAR MOVIMENTAÇÃO
    # ==============================

    conn.execute("""
    INSERT INTO movimentacoes (
        produto_id,
        produto_nome,
        tipo,
        quantidade,
        data_hora
    )
    VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
""", (
    produto_id,
    produto["nome"],
    tipo_movimentacao,
    1
))


    conn.commit()
    conn.close()


    return jsonify({
        "mensagem": "Quantidade atualizada!",
        "quantidade": nova_quantidade
    })


# ==============================
# EXCLUIR PRODUTO
# ==============================

@app.route(
    "/api/produtos/<int:produto_id>",
    methods=["DELETE"]
)
def excluir_produto(produto_id):

    conn = conectar_banco()


    produto = conn.execute("""
        SELECT *
        FROM produtos
        WHERE id = ?
    """, (produto_id,)).fetchone()


    if not produto:

        conn.close()

        return jsonify({
            "erro": "Produto não encontrado."
        }), 404


    conn.execute("""
        DELETE FROM produtos
        WHERE id = ?
    """, (produto_id,))


    conn.commit()
    conn.close()


    return jsonify({
        "mensagem": "Produto excluído com sucesso!"
    })


# ==============================
# LISTAR CATEGORIAS
# ==============================



@app.route("/api/categorias", methods=["POST"])
def adicionar_categoria():

    dados = request.get_json()

    nome = dados.get("nome", "").strip()


    if not nome:

        return jsonify({
            "erro": "Digite o nome da categoria."
        }), 400


    conn = conectar_banco()


    try:

        conn.execute("""
            INSERT INTO categorias (nome)
            VALUES (?)
        """, (nome,))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "erro": "Essa categoria já existe."
        }), 400


    conn.close()


    return jsonify({
        "mensagem": "Categoria criada com sucesso!"
    }), 201
# ==============================
# INICIAR SERVIDOR
# ==============================

# ==============================
# EDITAR CATEGORIA
# ==============================

@app.route("/api/categorias/<int:categoria_id>", methods=["PUT"])
def editar_categoria(categoria_id):

    dados = request.get_json()

    nome = dados.get("nome", "").strip()

    if not nome:
        return jsonify({
            "erro": "Digite o nome da categoria."
        }), 400

    conn = conectar_banco()

    categoria = conn.execute("""
        SELECT *
        FROM categorias
        WHERE id = ?
    """, (categoria_id,)).fetchone()

    if not categoria:
        conn.close()

        return jsonify({
            "erro": "Categoria não encontrada."
        }), 404

    existente = conn.execute("""
        SELECT *
        FROM categorias
        WHERE nome = ?
        AND id != ?
    """, (nome, categoria_id)).fetchone()

    if existente:
        conn.close()

        return jsonify({
            "erro": "Essa categoria já existe."
        }), 400

    conn.execute("""
        UPDATE categorias
        SET nome = ?
        WHERE id = ?
    """, (nome, categoria_id))

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": "Categoria atualizada com sucesso!"
    })


# ==============================
# EXCLUIR CATEGORIA
# ==============================

@app.route("/api/categorias/<int:categoria_id>", methods=["DELETE"])
def excluir_categoria(categoria_id):

    conn = conectar_banco()

    categoria = conn.execute("""
        SELECT *
        FROM categorias
        WHERE id = ?
    """, (categoria_id,)).fetchone()

    if not categoria:
        conn.close()

        return jsonify({
            "erro": "Categoria não encontrada."
        }), 404
    produtos = conn.execute("""
        SELECT COUNT(*) AS total
        FROM produtos
        WHERE categoria_id = ?
    """, (categoria_id,)).fetchone()
    

    if produtos["total"] > 0:
        conn.close()

        return jsonify({
            "erro": "Não é possível excluir esta categoria porque existem produtos usando ela."
        }), 400

    conn.execute("""
        DELETE FROM categorias
        WHERE id = ?
    """, (categoria_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": "Categoria excluída com sucesso!"
    })

# ==============================
# HISTÓRICO DE MOVIMENTAÇÕES
# ==============================

# ==============================
# HISTÓRICO DE MOVIMENTAÇÕES
# ==============================

@app.route(
    "/api/movimentacoes",
    methods=["GET"]
)
def listar_movimentacoes():

    conn = conectar_banco()

    movimentacoes = conn.execute("""
        SELECT
            id,
            produto_id,
            produto_nome,
            tipo,
            quantidade,
            data_hora
        FROM movimentacoes
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(movimentacao)
        for movimentacao in movimentacoes
    ])

# ==============================
# CADASTRAR USUÁRIO
# ==============================

@app.route("/api/usuarios", methods=["POST"])
def cadastrar_usuario():

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if session.get("perfil") != "Administrador":
        return jsonify({
            "erro": "Acesso permitido apenas para administradores."
        }), 403

    dados = request.get_json()

    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")
    perfil_id = dados.get("perfil_id")

    # ==============================
    # VALIDAÇÕES
    # ==============================

    if not nome or not email or not senha or not perfil_id:
        return jsonify({
            "erro": "Todos os campos são obrigatórios."
        }), 400

    if len(nome) > 100:
        return jsonify({
            "erro": "O nome do usuário deve ter no máximo 100 caracteres."
        }), 400

    padrao_email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(padrao_email, email):
        return jsonify({
            "erro": "Informe um endereço de e-mail válido."
        }), 400

    if len(email) > 150:
        return jsonify({
            "erro": "O e-mail deve ter no máximo 150 caracteres."
        }), 400

    if len(senha) < 6:
        return jsonify({
            "erro": "A senha deve possuir pelo menos 6 caracteres."
        }), 400

    conn = conectar_banco()
    
    conn = conectar_banco()

    perfil = conn.execute("""
        SELECT id
        FROM perfil
        WHERE id = ?
    """, (perfil_id,)).fetchone()

    if not perfil:
        conn.close()

        return jsonify({
            "erro": "Perfil não encontrado."
        }), 404

    senha_hash = generate_password_hash(senha)

    try:

        cursor = conn.execute("""
            INSERT INTO usuario (
                nome,
                email,
                senha,
                perfil_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            nome,
            email,
            senha_hash,
            perfil_id
        ))

        conn.commit()

        usuario_id = cursor.lastrowid

        conn.close()

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso.",
            "id": usuario_id
        }), 201

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "erro": "Já existe um usuário com este e-mail."
        }), 409

    # ==============================
# LISTAR USUÁRIOS
# ==============================

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if session.get("perfil") != "Administrador":
        return jsonify({
            "erro": "Acesso permitido apenas para administradores."
        }), 403
    conn = conectar_banco()

    usuarios = conn.execute("""
        SELECT
            usuario.id,
            usuario.nome,
            usuario.email,
            usuario.perfil_id,
            perfil.nome AS perfil
        FROM usuario
        INNER JOIN perfil
            ON usuario.perfil_id = perfil.id
        ORDER BY usuario.nome
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "perfil_id": usuario["perfil_id"],
            "perfil": usuario["perfil"]
        }
        for usuario in usuarios
    ])
# ==============================
# INICIAR SERVIDOR
# ==============================
@app.route("/api/login", methods=["POST"])
def login():

    dados = request.get_json()

    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({
            "erro": "E-mail e senha são obrigatórios."
        }), 400

    conn = conectar_banco()

    usuario = conn.execute("""
        SELECT
            usuario.id,
            usuario.nome,
            usuario.email,
            usuario.senha,
            usuario.perfil_id,
            perfil.nome AS perfil
        FROM usuario
        INNER JOIN perfil
            ON usuario.perfil_id = perfil.id
        WHERE usuario.email = ?
    """, (email,)).fetchone()

    conn.close()

    if not usuario:
        return jsonify({
            "erro": "E-mail ou senha inválidos."
        }), 401

    if not check_password_hash(
        usuario["senha"],
        senha
    ):
        return jsonify({
            "erro": "E-mail ou senha inválidos."
        }), 401

    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["usuario_email"] = usuario["email"]
    session["perfil_id"] = usuario["perfil_id"]
    session["perfil"] = usuario["perfil"]

    return jsonify({
        "mensagem": "Login realizado com sucesso.",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "perfil": usuario["perfil"]
        }
    }), 200

@app.route("/login")
def pagina_login():
    return render_template("login.html")

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "mensagem": "Logout realizado com sucesso."
    }), 200

@app.route("/api/perfis", methods=["GET"])
def listar_perfis():

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if session.get("perfil") != "Administrador":
        return jsonify({
            "erro": "Acesso permitido apenas para administradores."
        }), 403

    conn = conectar_banco()

    perfis = conn.execute("""
        SELECT
            id,
            nome,
            descricao
        FROM perfil
        ORDER BY nome
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "id": perfil["id"],
            "nome": perfil["nome"],
            "descricao": perfil["descricao"]
        }
        for perfil in perfis
    ])

@app.route("/api/sessao", methods=["GET"])
def obter_sessao():

    if "usuario_id" not in session:
        return jsonify({
            "autenticado": False
        }), 401

    return jsonify({
        "autenticado": True,
        "usuario": {
            "id": session["usuario_id"],
            "nome": session["usuario_nome"],
            "email": session["usuario_email"],
            "perfil_id": session["perfil_id"],
            "perfil": session["perfil"]
        }
    }), 200
if __name__ == "__main__":

    inicializar_banco()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )