from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "estoque.db"


# ==============================
# CONEXÃO COM O BANCO
# ==============================

def conectar_banco():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# INICIALIZAÇÃO DO BANCO
# ==============================

def inicializar_banco():
    conn = conectar_banco()

    # ==============================
    # TABELA DE PRODUTOS
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0,
            sku TEXT NOT NULL UNIQUE
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
    # TABELA DE MOVIMENTAÇÕES
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)


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


    conn.commit()
    conn.close()


# ==============================
# PÁGINA PRINCIPAL
# ==============================

@app.route("/")
def pagina_inicial():
    return render_template("index.html")


# ==============================
# LISTAR PRODUTOS
# ==============================

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():

    conn = conectar_banco()

    produtos = conn.execute("""
        SELECT *
        FROM produtos
        ORDER BY nome ASC
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


    # Conversão dos valores numéricos

    try:

        preco = float(preco)
        quantidade = int(quantidade)

    except (ValueError, TypeError):

        return jsonify({
            "erro": "Preço ou quantidade inválidos."
        }), 400


    # Impedir valores negativos

    if preco < 0 or quantidade < 0:

        return jsonify({
            "erro": "Preço e quantidade não podem ser negativos."
        }), 400


    conn = conectar_banco()

    try:

        conn.execute("""
            INSERT INTO produtos
            (
                nome,
                categoria,
                preco,
                quantidade,
                sku
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            nome,
            categoria,
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


    # Converter preço

    try:

        preco = float(preco)

    except (ValueError, TypeError):

        return jsonify({
            "erro": "Preço inválido."
        }), 400


    # Impedir preço negativo

    if preco < 0:

        return jsonify({
            "erro": "O preço não pode ser negativo."
        }), 400


    conn = conectar_banco()


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
            categoria = ?,
            preco = ?,
            sku = ?
        WHERE id = ?
    """, (
        nome,
        categoria,
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

        nova_quantidade = max(
            0,
            quantidade_atual - 1
        )

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

    conn.execute("""
        UPDATE produtos
        SET categoria = ?
        WHERE categoria = ?
    """, (nome, categoria["nome"]))

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
        WHERE categoria = ?
    """, (categoria["nome"],)).fetchone()

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
# INICIAR SERVIDOR
# ==============================


if __name__ == "__main__":

    inicializar_banco()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )