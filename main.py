from flask import Flask, jsonify, request, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re

from datetime import datetime

from flask import send_file

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)

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
# CONTROLE DE PERMISSÕES
# ==============================

def usuario_tem_perfil(*perfis_permitidos):
    """
    Verifica se existe um usuário autenticado
    e se o perfil dele está entre os permitidos.
    """

    if "usuario_id" not in session:
        return False

    return session.get("perfil") in perfis_permitidos

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

            FOREIGN KEY (perfil_id)
                REFERENCES perfil(id)
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

            FOREIGN KEY (categoria_id)
                REFERENCES categorias(id)
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
            usuario_id INTEGER,
            valor_unitario REAL,
            valor_total REAL,

            FOREIGN KEY (produto_id)
                REFERENCES produtos(id)
                ON DELETE SET NULL,

            FOREIGN KEY (usuario_id)
                REFERENCES usuario(id)
                ON DELETE SET NULL
        )
    """)
    # ==============================
    # TABELA DE RELATÓRIOS ARQUIVADOS
    # ==============================

    conn.execute("""
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
        )
    """)


    # ==============================
    # MIGRAÇÕES DA TABELA
    # MOVIMENTAÇÕES
    # ==============================

    # Essa verificação permite atualizar bancos
    # já existentes sem apagar os dados.

    colunas_movimentacoes = conn.execute("""
        PRAGMA table_info(movimentacoes)
    """).fetchall()

    nomes_colunas_movimentacoes = [
        coluna["name"]
        for coluna in colunas_movimentacoes
    ]


    # ==============================
    # MIGRAÇÃO - USUÁRIO
    # ==============================

    if "usuario_id" not in nomes_colunas_movimentacoes:

        conn.execute("""
            ALTER TABLE movimentacoes
            ADD COLUMN usuario_id INTEGER
        """)


    # ==============================
    # MIGRAÇÃO - VALOR UNITÁRIO
    # ==============================

    if "valor_unitario" not in nomes_colunas_movimentacoes:

        conn.execute("""
            ALTER TABLE movimentacoes
            ADD COLUMN valor_unitario REAL
        """)


    # ==============================
    # MIGRAÇÃO - VALOR TOTAL
    # ==============================

    if "valor_total" not in nomes_colunas_movimentacoes:

        conn.execute("""
            ALTER TABLE movimentacoes
            ADD COLUMN valor_total REAL
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
            "Gerente",
            "Gerencia produtos, categorias e movimentações de estoque"
        ),
        (
            "Funcionário",
            "Consulta produtos e realiza movimentações de estoque"
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
            INSERT OR IGNORE INTO categorias (
                nome
            )
            VALUES (?)
        """, (
            categoria,
        ))


    # ==============================
    # ADMINISTRADOR INICIAL
    # ==============================

    perfil_admin = conn.execute("""
        SELECT id
        FROM perfil
        WHERE nome = ?
    """, (
        "Administrador",
    )).fetchone()


    administrador = conn.execute("""
        SELECT id
        FROM usuario
        WHERE email = ?
    """, (
        "admin@easystock.com",
    )).fetchone()


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


    # ==============================
    # SALVAR ALTERAÇÕES
    # ==============================

    conn.commit()
    conn.close()
   # ==============================
# FORMATAR MOEDA PARA PDF
# ==============================

def formatar_moeda_pdf(valor):

    valor = float(
        valor or 0
    )

    valor_formatado = (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return (
        f"R$ {valor_formatado}"
    )


# ==============================
# FORMATAR DATA/HORA PARA PDF
# ==============================

def formatar_data_hora_pdf(data_hora):

    if not data_hora:
        return "—"

    try:

        data = datetime.strptime(
            data_hora,
            "%Y-%m-%d %H:%M:%S"
        )

        return data.strftime(
            "%d/%m/%Y %H:%M"
        )

    except ValueError:

        return data_hora
    # ==============================
# GERAR RELATÓRIO MENSAL EM PDF
# ==============================

def gerar_relatorio_mensal_pdf(ano, mes):

    nomes_meses = [
        "",
        "janeiro",
        "fevereiro",
        "marco",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro"
    ]

    nomes_meses_exibicao = [
        "",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro"
    ]


    # ==============================
    # VALIDAR PERÍODO
    # ==============================

    if mes < 1 or mes > 12:
        raise ValueError(
            "O mês informado é inválido."
        )


    periodo = f"{ano:04d}-{mes:02d}"


    # ==============================
    # CONSULTAR MOVIMENTAÇÕES
    # ==============================

    conn = conectar_banco()

    movimentacoes = conn.execute("""
        SELECT
            movimentacoes.id,
            movimentacoes.produto_nome,
            movimentacoes.tipo,
            movimentacoes.quantidade,
            movimentacoes.data_hora,
            movimentacoes.valor_unitario,
            movimentacoes.valor_total,
            usuario.nome AS usuario_nome

        FROM movimentacoes

        LEFT JOIN usuario
            ON usuario.id =
               movimentacoes.usuario_id

        WHERE strftime(
            '%Y-%m',
            movimentacoes.data_hora
        ) = ?

        ORDER BY
            movimentacoes.data_hora ASC,
            movimentacoes.id ASC
    """, (periodo,)).fetchall()

    conn.close()


    # ==============================
    # CRIAR PASTA DO RELATÓRIO
    # ==============================

    nome_pasta_mes = (
        f"{mes:02d}-"
        f"{nomes_meses[mes]}"
    )

    pasta_relatorios = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "relatorios",
        str(ano),
        nome_pasta_mes
    )

    os.makedirs(
        pasta_relatorios,
        exist_ok=True
    )


    # ==============================
    # CAMINHO DO PDF
    # ==============================

    nome_arquivo = (
        f"relatorio_movimentacoes_"
        f"{ano:04d}-{mes:02d}.pdf"
    )

    caminho_pdf = os.path.join(
        pasta_relatorios,
        nome_arquivo
    )


    # ==============================
    # CALCULAR RESUMO
    # ==============================

    total_entradas = 0
    total_saidas = 0

    itens_entrada = 0
    itens_saida = 0

    valor_entradas = 0.0
    valor_saidas = 0.0

    registros_sem_valor = 0


    for movimentacao in movimentacoes:

        quantidade = int(
            movimentacao["quantidade"] or 0
        )

        valor_total = (
            movimentacao["valor_total"]
        )


        if movimentacao["tipo"] == "entrada":

            total_entradas += 1
            itens_entrada += quantidade

            if valor_total is not None:
                valor_entradas += float(
                    valor_total
                )


        elif movimentacao["tipo"] == "saida":

            total_saidas += 1
            itens_saida += quantidade

            if valor_total is not None:
                valor_saidas += float(
                    valor_total
                )


        if valor_total is None:
            registros_sem_valor += 1


    # ==============================
    # DOCUMENTO
    # ==============================

    documento = SimpleDocTemplate(
        caminho_pdf,
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm
    )


    estilos = getSampleStyleSheet()


    estilo_titulo = ParagraphStyle(
        "TituloEasyStock",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=6
    )


    estilo_subtitulo = ParagraphStyle(
        "SubtituloEasyStock",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor(
            "#64748B"
        )
    )


    estilo_secao = ParagraphStyle(
        "SecaoEasyStock",
        parent=estilos["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=6,
        spaceAfter=8
    )


    elementos = []


    # ==============================
    # CABEÇALHO
    # ==============================

    elementos.append(
        Paragraph(
            "EasyStock",
            estilo_titulo
        )
    )

    elementos.append(
        Paragraph(
            "Relatório Mensal de Movimentações",
            estilo_subtitulo
        )
    )

    elementos.append(
        Paragraph(
            (
                f"Período: "
                f"{nomes_meses_exibicao[mes]}"
                f"/{ano}"
            ),
            estilo_subtitulo
        )
    )

    elementos.append(
        Paragraph(
            (
                "Gerado em: "
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
            ),
            estilo_subtitulo
        )
    )

    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )


    # ==============================
    # RESUMO
    # ==============================

    elementos.append(
        Paragraph(
            "Resumo do período",
            estilo_secao
        )
    )


    dados_resumo = [

        [
            "Movimentações",
            "Entradas",
            "Saídas",
            "Itens de entrada",
            "Itens de saída",
            "Valor das entradas",
            "Valor das saídas"
        ],

        [
            str(len(movimentacoes)),
            str(total_entradas),
            str(total_saidas),
            str(itens_entrada),
            str(itens_saida),
            formatar_moeda_pdf(
                valor_entradas
            ),
            formatar_moeda_pdf(
                valor_saidas
            )
        ]

    ]


    tabela_resumo = Table(
        dados_resumo,
        repeatRows=1
    )


    tabela_resumo.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#F1F5F9")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0F172A")
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CBD5E1")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )

        ])
    )


    elementos.append(
        tabela_resumo
    )

    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )


    # ==============================
    # MOVIMENTAÇÕES
    # ==============================

    elementos.append(
        Paragraph(
            "Movimentações registradas",
            estilo_secao
        )
    )


    dados_tabela = [[
        "Data e hora",
        "Produto",
        "Tipo",
        "Qtd.",
        "Valor unitário",
        "Valor total",
        "Usuário"
    ]]


    for movimentacao in movimentacoes:

        data_formatada = (
            formatar_data_hora_pdf(
                movimentacao["data_hora"]
            )
        )


        tipo = (
            "Entrada"
            if movimentacao["tipo"]
            == "entrada"
            else "Saída"
        )


        valor_unitario = (
            formatar_moeda_pdf(
                movimentacao[
                    "valor_unitario"
                ]
            )
            if movimentacao[
                "valor_unitario"
            ] is not None
            else "Não disponível"
        )


        valor_total = (
            formatar_moeda_pdf(
                movimentacao[
                    "valor_total"
                ]
            )
            if movimentacao[
                "valor_total"
            ] is not None
            else "Não disponível"
        )


        usuario = (
            movimentacao["usuario_nome"]
            or "Não identificado"
        )


        dados_tabela.append([

            data_formatada,

            movimentacao[
                "produto_nome"
            ] or "Produto removido",

            tipo,

            str(
                movimentacao[
                    "quantidade"
                ]
            ),

            valor_unitario,

            valor_total,

            usuario

        ])


    if len(movimentacoes) == 0:

        dados_tabela.append([
            "-",
            "Nenhuma movimentação registrada no período.",
            "-",
            "-",
            "-",
            "-",
            "-"
        ])


    tabela_movimentacoes = Table(
        dados_tabela,
        repeatRows=1,
        colWidths=[
            3.2 * cm,
            6.0 * cm,
            2.2 * cm,
            1.5 * cm,
            3.2 * cm,
            3.2 * cm,
            4.0 * cm
        ]
    )


    tabela_movimentacoes.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0F172A")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#CBD5E1")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ALIGN",
                (2, 1),
                (5, -1),
                "CENTER"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F8FAFC")
                ]
            )

        ])
    )


    elementos.append(
        tabela_movimentacoes
    )


    # ==============================
    # OBSERVAÇÃO SOBRE DADOS ANTIGOS
    # ==============================

    if registros_sem_valor > 0:

        elementos.append(
            Spacer(
                1,
                0.4 * cm
            )
        )

        elementos.append(
            Paragraph(
                (
                    f"Observação: {registros_sem_valor} "
                    "movimentação(ões) deste período "
                    "não possui(em) valor financeiro "
                    "histórico registrado."
                ),
                estilos["Normal"]
            )
        )


    # ==============================
    # GERAR PDF
    # ==============================

    documento.build(
        elementos
    )


    return caminho_pdf
# ==============================
# ARQUIVAR RELATÓRIO DO
# MÊS ANTERIOR AUTOMATICAMENTE
# ==============================

def arquivar_relatorio_mes_anterior():

    agora = datetime.now()

    # ==============================
    # CALCULAR MÊS ANTERIOR
    # ==============================

    if agora.month == 1:

        mes_anterior = 12
        ano_anterior = agora.year - 1

    else:

        mes_anterior = agora.month - 1
        ano_anterior = agora.year


    nomes_meses = [
        "",
        "janeiro",
        "fevereiro",
        "marco",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro"
    ]


    # ==============================
    # LOCAL DO RELATÓRIO
    # ==============================

    nome_pasta_mes = (
        f"{mes_anterior:02d}-"
        f"{nomes_meses[mes_anterior]}"
    )


    pasta_relatorio = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "relatorios",
        str(ano_anterior),
        nome_pasta_mes
    )


    nome_arquivo = (
        "relatorio_movimentacoes_"
        f"{ano_anterior:04d}-"
        f"{mes_anterior:02d}.pdf"
    )


    caminho_pdf = os.path.join(
        pasta_relatorio,
        nome_arquivo
    )


    # ==============================
    # VERIFICAR SE JÁ EXISTE
    # ==============================

    if os.path.exists(
        caminho_pdf
    ):

        return {
            "gerado": False,
            "motivo":
                "Relatório já existente.",
            "caminho":
                caminho_pdf
        }


    # ==============================
    # GERAR AUTOMATICAMENTE
    # ==============================

    caminho_gerado = (
        gerar_relatorio_mensal_pdf(
            ano_anterior,
            mes_anterior
        )
    )


    # ==============================
    # REGISTRAR NO BANCO
    # ==============================

    conn = conectar_banco()

    try:

        conn.execute("""
            INSERT OR IGNORE INTO
            relatorios_arquivados (
                ano,
                mes,
                nome_arquivo,
                caminho_arquivo,
                tipo_geracao,
                data_geracao,
                usuario_id
            )
            VALUES (
                ?, ?, ?, ?, ?,
                datetime('now', 'localtime'),
                ?
            )
        """, (
            ano_anterior,
            mes_anterior,
            nome_arquivo,
            caminho_gerado,
            "automatico",
            None
        ))


        conn.commit()


    finally:

        conn.close()


    # ==============================
    # RESULTADO
    # ==============================

    return {
        "gerado": True,
        "motivo":
            "Relatório mensal arquivado "
            "automaticamente.",
        "caminho":
            caminho_gerado
    }
# ==============================
# PÁGINA PRINCIPAL
# ==============================

@app.route("/")
def pagina_inicial():

    if "usuario_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        pagina_ativa="dashboard"
    )
@app.route("/produtos")
def pagina_produtos():

    if "usuario_id" not in session:
        return redirect("/login")

    return render_template(
        "produtos.html",
        pagina_ativa="produtos"
    )

@app.route("/categorias")
def pagina_categorias():
    if "usuario_id" not in session:
        return redirect("/login")

    return render_template(
        "categorias.html",
        pagina_ativa="categorias"
    )

@app.route("/movimentacoes")
def pagina_movimentacoes():
    if "usuario_id" not in session:
        return redirect("/login")

    return render_template(
        "movimentacoes.html",
        pagina_ativa="movimentacoes"
    )
@app.route("/historico")
def pagina_historico():

    if "usuario_id" not in session:
        return redirect("/login")

    return render_template(
        "historico.html",
        pagina_ativa="historico"
    )
@app.route("/usuarios")
def pagina_usuarios():

    if "usuario_id" not in session:
        return redirect("/login")

    if session.get("perfil") != "Administrador":
        return redirect("/")

    return render_template(
        "usuarios.html",
        pagina_ativa="usuarios"
    )
@app.route(
    "/api/usuarios/<int:usuario_id>",
    methods=["PUT"]
)
def editar_usuario(usuario_id):

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if session.get("perfil") != "Administrador":
        return jsonify({
            "erro": "Acesso permitido apenas para administradores."
        }), 403

    dados = request.get_json() or {}

    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip().lower()
    perfil_id = dados.get("perfil_id")

    # ==============================
    # VALIDAÇÕES
    # ==============================

    if not nome or not email or not perfil_id:
        return jsonify({
            "erro": "Nome, e-mail e perfil são obrigatórios."
        }), 400

    if len(nome) > 100:
        return jsonify({
            "erro":
                "O nome do usuário deve ter no máximo 100 caracteres."
        }), 400

    padrao_email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(padrao_email, email):
        return jsonify({
            "erro": "Informe um endereço de e-mail válido."
        }), 400

    if len(email) > 150:
        return jsonify({
            "erro":
                "O e-mail deve ter no máximo 150 caracteres."
        }), 400

    conn = conectar_banco()

    # ==============================
    # VERIFICAR USUÁRIO
    # ==============================

    usuario = conn.execute("""
        SELECT id
        FROM usuario
        WHERE id = ?
    """, (usuario_id,)).fetchone()

    if not usuario:
        conn.close()

        return jsonify({
            "erro": "Usuário não encontrado."
        }), 404

    # ==============================
    # VERIFICAR PERFIL
    # ==============================

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

    # ==============================
    # VERIFICAR E-MAIL DUPLICADO
    # ==============================

    email_existente = conn.execute("""
        SELECT id
        FROM usuario
        WHERE email = ?
          AND id != ?
    """, (
        email,
        usuario_id
    )).fetchone()

    if email_existente:
        conn.close()

        return jsonify({
            "erro":
                "Já existe outro usuário com este e-mail."
        }), 409

    # ==============================
    # PROTEGER ÚLTIMO ADMINISTRADOR
    # ==============================

    usuario_atual = conn.execute("""
        SELECT
            usuario.id,
            perfil.nome AS perfil
        FROM usuario
        INNER JOIN perfil
            ON usuario.perfil_id = perfil.id
        WHERE usuario.id = ?
    """, (usuario_id,)).fetchone()

    novo_perfil = conn.execute("""
        SELECT nome
        FROM perfil
        WHERE id = ?
    """, (perfil_id,)).fetchone()

    if (
        usuario_atual
        and usuario_atual["perfil"] == "Administrador"
        and novo_perfil
        and novo_perfil["nome"] != "Administrador"
    ):

        total_administradores = conn.execute("""
            SELECT COUNT(*) AS total
            FROM usuario
            INNER JOIN perfil
                ON usuario.perfil_id = perfil.id
            WHERE perfil.nome = 'Administrador'
        """).fetchone()["total"]

        if total_administradores <= 1:
            conn.close()

            return jsonify({
                "erro":
                    "Não é possível alterar o perfil do último administrador do sistema."
            }), 400
    # ==============================
    # ATUALIZAR
    # ==============================

    conn.execute("""
        UPDATE usuario
        SET
            nome = ?,
            email = ?,
            perfil_id = ?
        WHERE id = ?
    """, (
        nome,
        email,
        perfil_id,
        usuario_id
    ))

    conn.commit()
    conn.close()

    # Se o administrador editou a própria conta,
    # mantém os dados da sessão atualizados.
    if session.get("usuario_id") == usuario_id:

        session["usuario_nome"] = nome
        session["usuario_email"] = email
        session["perfil_id"] = perfil_id

        conn = conectar_banco()

        perfil_atualizado = conn.execute("""
            SELECT nome
            FROM perfil
            WHERE id = ?
        """, (perfil_id,)).fetchone()

        conn.close()

        if perfil_atualizado:
            session["perfil"] = perfil_atualizado["nome"]

    return jsonify({
        "mensagem": "Usuário atualizado com sucesso."
    }), 200

@app.route(
    "/api/usuarios/<int:usuario_id>",
    methods=["DELETE"]
)
def excluir_usuario(usuario_id):

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if session.get("perfil") != "Administrador":
        return jsonify({
            "erro":
                "Acesso permitido apenas para administradores."
        }), 403

    # Não permite excluir a própria conta
    if session.get("usuario_id") == usuario_id:
        return jsonify({
            "erro":
                "Você não pode excluir o usuário que está conectado."
        }), 400

    conn = conectar_banco()

    # ==============================
    # VERIFICAR USUÁRIO
    # ==============================

    usuario = conn.execute("""
        SELECT
            usuario.id,
            usuario.nome,
            usuario.perfil_id,
            perfil.nome AS perfil
        FROM usuario
        INNER JOIN perfil
            ON usuario.perfil_id = perfil.id
        WHERE usuario.id = ?
    """, (usuario_id,)).fetchone()

    if not usuario:
        conn.close()

        return jsonify({
            "erro": "Usuário não encontrado."
        }), 404

    # ==============================
    # PROTEGER ÚLTIMO ADMINISTRADOR
    # ==============================

    if usuario["perfil"] == "Administrador":

        total_administradores = conn.execute("""
            SELECT COUNT(*) AS total
            FROM usuario
            INNER JOIN perfil
                ON usuario.perfil_id = perfil.id
            WHERE perfil.nome = 'Administrador'
        """).fetchone()["total"]

        if total_administradores <= 1:
            conn.close()

            return jsonify({
                "erro":
                    "Não é possível excluir o último administrador do sistema."
            }), 400

    # ==============================
    # EXCLUIR USUÁRIO
    # ==============================

    conn.execute("""
        DELETE FROM usuario
        WHERE id = ?
    """, (usuario_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem":
            "Usuário excluído com sucesso."
    }), 200
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
        SELECT
            categorias.id,
            categorias.nome,
            COUNT(produtos.id) AS quantidade_produtos

        FROM categorias

        LEFT JOIN produtos
            ON produtos.categoria_id = categorias.id

        GROUP BY
            categorias.id,
            categorias.nome

        ORDER BY
            categorias.nome ASC
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

    # ==============================
    # CONTROLE DE PERMISSÃO
    # ==============================

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if not usuario_tem_perfil(
        "Administrador",
        "Gerente"
    ):
        return jsonify({
            "erro":
                "Você não possui permissão para cadastrar produtos."
        }), 403
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

    # ==============================
    # CONTROLE DE PERMISSÃO
    # ==============================

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if not usuario_tem_perfil(
        "Administrador",
        "Gerente"
    ):
        return jsonify({
            "erro":
                "Você não possui permissão para editar produtos."
        }), 403
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

    # ==============================
    # AUTENTICAÇÃO
    # ==============================

    if "usuario_id" not in session:

        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401


    dados = request.get_json() or {}

    operacao = dados.get("operacao")

    # Se nenhuma quantidade for informada,
    # mantém o comportamento de +1 / -1.
    quantidade = dados.get("quantidade", 1)


    # ==============================
    # VALIDAR OPERAÇÃO
    # ==============================

    if operacao not in [
        "adicionar",
        "remover"
    ]:

        return jsonify({
            "erro": "Operação inválida."
        }), 400


    # ==============================
    # VALIDAR QUANTIDADE
    # ==============================

    try:

        quantidade = int(quantidade)

    except (TypeError, ValueError):

        return jsonify({
            "erro":
                "Informe uma quantidade válida."
        }), 400


    if quantidade <= 0:

        return jsonify({
            "erro":
                "A quantidade deve ser maior que zero."
        }), 400


    conn = conectar_banco()


    # ==============================
    # BUSCAR PRODUTO
    # ==============================

    produto = conn.execute("""
        SELECT
            id,
            nome,
            preco,
            quantidade
        FROM produtos
        WHERE id = ?
    """, (
        produto_id,
    )).fetchone()


    if not produto:

        conn.close()

        return jsonify({
            "erro": "Produto não encontrado."
        }), 404


    quantidade_atual = int(
        produto["quantidade"]
    )

    valor_unitario = float(
        produto["preco"]
    )


    # ==============================
    # CALCULAR NOVO ESTOQUE
    # ==============================

    if operacao == "adicionar":

        nova_quantidade = (
            quantidade_atual +
            quantidade
        )

        tipo_movimentacao = "entrada"

    else:

        if quantidade > quantidade_atual:

            conn.close()

            return jsonify({
                "erro":
                    "Não é possível realizar a saída. "
                    "A quantidade informada é maior "
                    "que o estoque disponível."
            }), 400

        nova_quantidade = (
            quantidade_atual -
            quantidade
        )

        tipo_movimentacao = "saida"


    # ==============================
    # CALCULAR VALOR DA MOVIMENTAÇÃO
    # ==============================

    valor_total = (
        valor_unitario *
        quantidade
    )


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
            data_hora,
            usuario_id,
            valor_unitario,
            valor_total
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            datetime(
                'now',
                'localtime'
            ),
            ?,
            ?,
            ?
        )
    """, (
        produto_id,
        produto["nome"],
        tipo_movimentacao,
        quantidade,
        session.get("usuario_id"),
        valor_unitario,
        valor_total
    ))


    # ==============================
    # SALVAR ALTERAÇÕES
    # ==============================

    conn.commit()
    conn.close()


    # ==============================
    # RESPOSTA
    # ==============================

    return jsonify({
        "mensagem":
            "Movimentação registrada com sucesso!",
        "quantidade":
            nova_quantidade,
        "valor_unitario":
            round(valor_unitario, 2),
        "valor_total":
            round(valor_total, 2)
    }), 200

# ==============================
# EXCLUIR PRODUTO
# ==============================

@app.route(
    "/api/produtos/<int:produto_id>",
    methods=["DELETE"]
)
def excluir_produto(produto_id):

    # ==============================
    # CONTROLE DE PERMISSÃO
    # ==============================

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if not usuario_tem_perfil(
        "Administrador",
        "Gerente"
    ):
        return jsonify({
            "erro":
                "Você não possui permissão para excluir produtos."
        }), 403
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
    # ==============================
    # CONTROLE DE PERMISSÃO
    # ==============================

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if not usuario_tem_perfil(
        "Administrador",
        "Gerente"
    ):
        return jsonify({
            "erro":
                "Você não possui permissão para cadastrar categorias."
        }), 403

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
    # ==============================
    # CONTROLE DE PERMISSÃO
    # ==============================

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if not usuario_tem_perfil(
        "Administrador",
        "Gerente"
    ):
        return jsonify({
            "erro":
                "Você não possui permissão para editar categorias."
        }), 403

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
    # ==============================
    # CONTROLE DE PERMISSÃO
    # ==============================

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    if not usuario_tem_perfil(
        "Administrador",
        "Gerente"
    ):
        return jsonify({
            "erro":
                "Você não possui permissão para excluir categorias."
        }), 403

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


    if "usuario_id" not in session:

        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401


    conn = conectar_banco()


    movimentacoes = conn.execute("""
        SELECT
            movimentacoes.id,
            movimentacoes.produto_id,
            movimentacoes.produto_nome,
            movimentacoes.tipo,
            movimentacoes.quantidade,
            movimentacoes.data_hora,
            movimentacoes.usuario_id,
            movimentacoes.valor_unitario,
            movimentacoes.valor_total,
            usuario.nome AS usuario_nome

        FROM movimentacoes

        LEFT JOIN usuario
            ON usuario.id =
               movimentacoes.usuario_id

        ORDER BY movimentacoes.id DESC
    """).fetchall()


    conn.close()


    return jsonify([
        dict(movimentacao)
        for movimentacao in movimentacoes
    ])
## ==============================
# RELATÓRIO MENSAL DE MOVIMENTAÇÕES
# ==============================

@app.route(
    "/api/relatorios/movimentacoes",
    methods=["GET"]
)
def relatorio_movimentacoes():

    # ==============================
    # AUTENTICAÇÃO
    # ==============================

    if "usuario_id" not in session:

        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    # ==============================
    # PERMISSÃO
    # SOMENTE ADMINISTRADOR
    # ==============================

    if session.get("perfil") != "Administrador":

        return jsonify({
            "erro":
                "Acesso permitido apenas para administradores."
        }), 403


    # ==============================
    # PARÂMETROS
    # ==============================

    mes = request.args.get(
        "mes",
        type=int
    )

    ano = request.args.get(
        "ano",
        type=int
    )


    # ==============================
    # VALIDAR MÊS
    # ==============================

    if mes is None or mes < 1 or mes > 12:

        return jsonify({
            "erro":
                "Informe um mês válido entre 1 e 12."
        }), 400


    # ==============================
    # VALIDAR ANO
    # ==============================

    if ano is None or ano < 2000 or ano > 2100:

        return jsonify({
            "erro":
                "Informe um ano válido."
        }), 400


    # ==============================
    # GERAR PDF
    # ==============================

    try:

        caminho_pdf = (
            gerar_relatorio_mensal_pdf(
                ano,
                mes
            )
        )


        nome_arquivo = (
            f"relatorio_movimentacoes_"
            f"{ano:04d}-{mes:02d}.pdf"
        )


        # ==============================
        # REGISTRAR RELATÓRIO ARQUIVADO
        # ==============================

        conn = conectar_banco()

        try:

            conn.execute("""
                INSERT OR IGNORE INTO relatorios_arquivados (
                    ano,
                    mes,
                    nome_arquivo,
                    caminho_arquivo,
                    tipo_geracao,
                    data_geracao,
                    usuario_id
                )
                VALUES (
                    ?, ?, ?, ?, ?,
                    datetime('now', 'localtime'),
                    ?
                )
            """, (
                ano,
                mes,
                nome_arquivo,
                caminho_pdf,
                "manual",
                session.get("usuario_id")
            ))

            conn.commit()

        finally:

            conn.close()


        # ==============================
        # ENVIAR PARA DOWNLOAD
        # ==============================

        return send_file(
            caminho_pdf,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype="application/pdf"
        )


    except Exception as erro:

        print(
            "Erro ao gerar relatório:",
            erro
        )

        return jsonify({
            "erro":
                "Não foi possível gerar "
                "o relatório solicitado."
        }), 500
def relatorio_movimentacoes():

    # ==============================
    # AUTENTICAÇÃO
    # ==============================

    if "usuario_id" not in session:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401


    # ==============================
    # PERMISSÃO
    # ==============================

    if session.get("perfil") != "Administrador":
        return jsonify({
            "erro":
                "Acesso permitido apenas para administradores."
        }), 403


    # ==============================
    # PARÂMETROS
    # ==============================

    mes = request.args.get("mes", type=int)
    ano = request.args.get("ano", type=int)


    if mes is None or mes < 1 or mes > 12:
        return jsonify({
            "erro":
                "Informe um mês válido entre 1 e 12."
        }), 400


    if ano is None or ano < 2000 or ano > 2100:
        return jsonify({
            "erro": "Informe um ano válido."
        }), 400


    periodo = f"{ano:04d}-{mes:02d}"


    # ==============================
    # CONSULTA
    # ==============================

    conn = conectar_banco()

    movimentacoes = conn.execute("""
        SELECT
            movimentacoes.id,
            movimentacoes.produto_id,
            movimentacoes.produto_nome,
            movimentacoes.tipo,
            movimentacoes.quantidade,
            movimentacoes.data_hora,
            movimentacoes.usuario_id,
            movimentacoes.valor_unitario,
            movimentacoes.valor_total,
            usuario.nome AS usuario_nome

        FROM movimentacoes

        LEFT JOIN usuario
            ON usuario.id = movimentacoes.usuario_id

        WHERE strftime(
            '%Y-%m',
            movimentacoes.data_hora
        ) = ?

        ORDER BY
            movimentacoes.data_hora ASC,
            movimentacoes.id ASC
    """, (periodo,)).fetchall()

    conn.close()


    # ==============================
    # RESUMO
    # ==============================

    total_movimentacoes = len(movimentacoes)

    movimentacoes_entrada = 0
    movimentacoes_saida = 0

    itens_entrada = 0
    itens_saida = 0

    valor_entradas = 0.0
    valor_saidas = 0.0

    movimentacoes_sem_valor = 0

    dados_movimentacoes = []


    for movimentacao in movimentacoes:

        tipo = movimentacao["tipo"]

        quantidade = int(
            movimentacao["quantidade"] or 0
        )

        valor_unitario = (
            movimentacao["valor_unitario"]
        )

        valor_total = (
            movimentacao["valor_total"]
        )


        if tipo == "entrada":

            movimentacoes_entrada += 1
            itens_entrada += quantidade

            if valor_total is not None:
                valor_entradas += float(
                    valor_total
                )


        elif tipo == "saida":

            movimentacoes_saida += 1
            itens_saida += quantidade

            if valor_total is not None:
                valor_saidas += float(
                    valor_total
                )


        if valor_total is None:
            movimentacoes_sem_valor += 1


        dados_movimentacoes.append({

            "id":
                movimentacao["id"],

            "produto_id":
                movimentacao["produto_id"],

            "produto_nome":
                movimentacao["produto_nome"],

            "tipo":
                tipo,

            "quantidade":
                quantidade,

            "data_hora":
                movimentacao["data_hora"],

            "usuario_id":
                movimentacao["usuario_id"],

            "usuario_nome":
                movimentacao["usuario_nome"],

            "valor_unitario":
                round(
                    float(valor_unitario),
                    2
                )
                if valor_unitario is not None
                else None,

            "valor_total":
                round(
                    float(valor_total),
                    2
                )
                if valor_total is not None
                else None

        })


    nomes_meses = [
        "",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro"
    ]


    # ==============================
    # RESPOSTA
    # ==============================

    return jsonify({

        "periodo": {
            "mes": mes,
            "ano": ano,
            "mes_nome": nomes_meses[mes],
            "descricao":
                f"{nomes_meses[mes]}/{ano}"
        },

        "resumo": {
            "total_movimentacoes":
                total_movimentacoes,

            "movimentacoes_entrada":
                movimentacoes_entrada,

            "movimentacoes_saida":
                movimentacoes_saida,

            "itens_entrada":
                itens_entrada,

            "itens_saida":
                itens_saida,

            "valor_entradas":
                round(valor_entradas, 2),

            "valor_saidas":
                round(valor_saidas, 2),

            "movimentacoes_sem_valor":
                movimentacoes_sem_valor
        },

        "movimentacoes":
            dados_movimentacoes

    }), 200
# ==============================
# EXPORTAR RELATÓRIO MENSAL EM PDF
# ==============================

@app.route(
    "/api/relatorios/movimentacoes/pdf",
    methods=["GET"]
)
def exportar_relatorio_movimentacoes_pdf():

    # ==============================
    # AUTENTICAÇÃO
    # ==============================

    if "usuario_id" not in session:

        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401


    # ==============================
    # SOMENTE ADMINISTRADOR
    # ==============================

    if session.get("perfil") != "Administrador":

        return jsonify({
            "erro":
                "Acesso permitido somente "
                "para administradores."
        }), 403


    # ==============================
    # RECEBER MÊS E ANO
    # ==============================

    mes = request.args.get(
        "mes",
        type=int
    )

    ano = request.args.get(
        "ano",
        type=int
    )


    # ==============================
    # VALIDAR PARÂMETROS
    # ==============================

    if mes is None or ano is None:

        return jsonify({
            "erro":
                "Informe o mês e o ano "
                "do relatório."
        }), 400


    if mes < 1 or mes > 12:

        return jsonify({
            "erro": "Mês inválido."
        }), 400


    if ano < 2000 or ano > 2100:

        return jsonify({
            "erro": "Ano inválido."
        }), 400


    try:

        # ==============================
        # GERAR PDF
        # ==============================

        caminho_pdf = gerar_relatorio_mensal_pdf(
            ano,
            mes
        )


        # ==============================
        # NOME DO ARQUIVO
        # ==============================

        nome_arquivo = os.path.basename(
            caminho_pdf
        )


        # ==============================
        # REGISTRAR RELATÓRIO MANUAL
        # ==============================

        conn = conectar_banco()

        try:

            conn.execute("""
                INSERT OR IGNORE INTO relatorios_arquivados (
                    ano,
                    mes,
                    nome_arquivo,
                    caminho_arquivo,
                    tipo_geracao,
                    data_geracao,
                    usuario_id
                )
                VALUES (
                    ?, ?, ?, ?, ?,
                    datetime('now', 'localtime'),
                    ?
                )
            """, (
                ano,
                mes,
                nome_arquivo,
                caminho_pdf,
                "manual",
                session.get("usuario_id")
            ))

            conn.commit()

        finally:

            conn.close()


        # ==============================
        # ENVIAR PDF PARA DOWNLOAD
        # ==============================

        return send_file(
            caminho_pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=nome_arquivo
        )


    except ValueError as erro:

        return jsonify({
            "erro": str(erro)
        }), 400


    except Exception as erro:

        print(
            "Erro ao exportar relatório mensal:",
            erro
        )

        return jsonify({
            "erro":
                "Não foi possível gerar "
                "o relatório mensal."
        }), 500

# ==============================
# LISTAR RELATÓRIOS ARQUIVADOS
# ==============================

@app.route(
    "/api/relatorios/arquivados",
    methods=["GET"]
)
def listar_relatorios_arquivados():

    # ==============================
    # AUTENTICAÇÃO
    # ==============================

    if "usuario_id" not in session:

        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401


    # ==============================
    # SOMENTE ADMINISTRADOR
    # ==============================

    if session.get("perfil") != "Administrador":

        return jsonify({
            "erro":
                "Acesso permitido somente "
                "para administradores."
        }), 403


    # ==============================
    # CONSULTAR BANCO
    # ==============================

    conn = conectar_banco()

    relatorios = conn.execute("""
        SELECT
            relatorios_arquivados.id,
            relatorios_arquivados.ano,
            relatorios_arquivados.mes,
            relatorios_arquivados.nome_arquivo,
            relatorios_arquivados.caminho_arquivo,
            relatorios_arquivados.tipo_geracao,
            relatorios_arquivados.data_geracao,
            relatorios_arquivados.usuario_id,

            usuario.nome AS usuario_nome

        FROM relatorios_arquivados

        LEFT JOIN usuario
            ON usuario.id =
               relatorios_arquivados.usuario_id

        ORDER BY
            relatorios_arquivados.ano DESC,
            relatorios_arquivados.mes DESC
    """).fetchall()

    conn.close()


    # ==============================
    # NOMES DOS MESES
    # ==============================

    nomes_meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }


    # ==============================
    # PREPARAR RESPOSTA
    # ==============================

    dados = []


    for relatorio in relatorios:

        mes = relatorio["mes"]
        ano = relatorio["ano"]

        mes_nome = nomes_meses.get(
            mes,
            str(mes)
        )


        # ==========================
        # FORMATAR DATA
        # ==========================

        data_formatada = (
            relatorio["data_geracao"]
            or ""
        )


        if data_formatada:

            try:

                data_objeto = datetime.strptime(
                    data_formatada,
                    "%Y-%m-%d %H:%M:%S"
                )

                data_formatada = (
                    data_objeto.strftime(
                        "%d/%m/%Y %H:%M"
                    )
                )

            except ValueError:

                pass


        # ==========================
        # TIPO DE GERAÇÃO
        # ==========================

        tipo_geracao = (
            relatorio["tipo_geracao"]
            or "manual"
        )


        # ==========================
        # ADICIONAR À RESPOSTA
        # ==========================

        dados.append({

            "id":
                relatorio["id"],

            "ano":
                ano,

            "mes":
                mes,

            "mes_nome":
                mes_nome,

            "periodo":
                f"{mes_nome} de {ano}",

            "nome_arquivo":
                relatorio["nome_arquivo"],

            "tipo_geracao":
                tipo_geracao,

            "data_geracao":
                data_formatada,

            # Mantemos este campo também
            # por compatibilidade com o
            # JavaScript atual.
            "data_arquivo":
                data_formatada,

            "usuario_id":
                relatorio["usuario_id"],

            "usuario_nome":
                relatorio["usuario_nome"]

        })


    return jsonify(dados)

# ==============================
# BAIXAR RELATÓRIO ARQUIVADO
# ==============================

@app.route(
    "/api/relatorios/arquivados/<int:ano>/<int:mes>/<path:nome_arquivo>",
    methods=["GET"]
)
def baixar_relatorio_arquivado(
    ano,
    mes,
    nome_arquivo
):

    # ==============================
    # AUTENTICAÇÃO
    # ==============================

    if "usuario_id" not in session:

        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401


    # ==============================
    # SOMENTE ADMINISTRADOR
    # ==============================

    if session.get("perfil") != "Administrador":

        return jsonify({
            "erro":
                "Acesso permitido somente "
                "para administradores."
        }), 403


    # ==============================
    # VALIDAR MÊS
    # ==============================

    if mes < 1 or mes > 12:

        return jsonify({
            "erro": "Mês inválido."
        }), 400


    nomes_meses = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro"
    }


    # ==============================
    # SEGURANÇA DO NOME DO ARQUIVO
    # ==============================

    # Impede tentativa de navegar para
    # outras pastas usando ../

    nome_seguro = os.path.basename(
        nome_arquivo
    )


    if nome_seguro != nome_arquivo:

        return jsonify({
            "erro": "Nome de arquivo inválido."
        }), 400


    if not nome_seguro.lower().endswith(
        ".pdf"
    ):

        return jsonify({
            "erro": "Arquivo inválido."
        }), 400


    # ==============================
    # LOCALIZAR ARQUIVO
    # ==============================

    pasta_relatorios = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "relatorios"
    )


    pasta_mes = (
        f"{mes:02d}-"
        f"{nomes_meses[mes]}"
    )


    caminho_arquivo = os.path.join(
        pasta_relatorios,
        str(ano),
        pasta_mes,
        nome_seguro
    )


    # ==============================
    # VERIFICAR EXISTÊNCIA
    # ==============================

    if not os.path.isfile(
        caminho_arquivo
    ):

        return jsonify({
            "erro":
                "Relatório não encontrado."
        }), 404


    # ==============================
    # ENVIAR PDF
    # ==============================

    return send_file(
        caminho_arquivo,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nome_seguro
    )

# ==============================
# RESUMO FINANCEIRO
# ==============================

@app.route(
    "/api/dashboard/financeiro",
    methods=["GET"]
)
def dashboard_financeiro():

    # ==============================
    # AUTENTICAÇÃO
    # ==============================

    if "usuario_id" not in session:

        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401


    # ==============================
    # PERMISSÃO
    # ==============================

    if session.get("perfil") != "Administrador":

        return jsonify({
            "erro":
                "Acesso permitido apenas para administradores."
        }), 403


    conn = conectar_banco()


    # ==============================
    # VALOR ATUAL DO ESTOQUE
    # ==============================

    valor_estoque = conn.execute("""
        SELECT
            COALESCE(
                SUM(preco * quantidade),
                0
            ) AS total
        FROM produtos
    """).fetchone()["total"]


    # ==============================
    # VALOR TOTAL DAS ENTRADAS
    # ==============================

    valor_entradas = conn.execute("""
        SELECT
            COALESCE(
                SUM(valor_total),
                0
            ) AS total
        FROM movimentacoes
        WHERE tipo = 'entrada'
          AND valor_total IS NOT NULL
    """).fetchone()["total"]


    # ==============================
    # VALOR TOTAL DAS SAÍDAS
    # ==============================

    valor_saidas = conn.execute("""
        SELECT
            COALESCE(
                SUM(valor_total),
                0
            ) AS total
        FROM movimentacoes
        WHERE tipo = 'saida'
          AND valor_total IS NOT NULL
    """).fetchone()["total"]


    # ==============================
    # ÚLTIMOS 7 DIAS
    # ==============================

    dados_ultimos_dias = conn.execute("""
        WITH RECURSIVE dias(data) AS (

            SELECT date(
                'now',
                'localtime',
                '-6 days'
            )

            UNION ALL

            SELECT date(
                data,
                '+1 day'
            )
            FROM dias
            WHERE data < date(
                'now',
                'localtime'
            )
        )

        SELECT
            dias.data,

            COALESCE(
                SUM(
                    CASE
                        WHEN movimentacoes.tipo = 'entrada'
                        THEN movimentacoes.valor_total
                        ELSE 0
                    END
                ),
                0
            ) AS entradas,

            COALESCE(
                SUM(
                    CASE
                        WHEN movimentacoes.tipo = 'saida'
                        THEN movimentacoes.valor_total
                        ELSE 0
                    END
                ),
                0
            ) AS saidas

        FROM dias

        LEFT JOIN movimentacoes
            ON date(
                movimentacoes.data_hora
            ) = dias.data
            AND movimentacoes.valor_total
                IS NOT NULL

        GROUP BY dias.data

        ORDER BY dias.data ASC
    """).fetchall()


    conn.close()


    # ==============================
    # FORMATAR DADOS DO GRÁFICO
    # ==============================

    grafico_7_dias = []

    for dia in dados_ultimos_dias:

        grafico_7_dias.append({
            "data": dia["data"],
            "entradas": round(
                float(dia["entradas"] or 0),
                2
            ),
            "saidas": round(
                float(dia["saidas"] or 0),
                2
            )
        })


    # ==============================
    # RESPOSTA
    # ==============================

    return jsonify({

        "valor_estoque":
            round(
                float(valor_estoque or 0),
                2
            ),

        "valor_entradas":
            round(
                float(valor_entradas or 0),
                2
            ),

        "valor_saidas":
            round(
                float(valor_saidas or 0),
                2
            ),

        "grafico_7_dias":
            grafico_7_dias

    }), 200

    # ==============================
    # PERMISSÃO
    # ==============================

    if session.get("perfil") != "Administrador":

        return jsonify({
            "erro":
                "Acesso permitido apenas para administradores."
        }), 403


    conn = conectar_banco()


    # ==============================
    # VALOR ATUAL DO ESTOQUE
    # ==============================

    valor_estoque = conn.execute("""
        SELECT
            COALESCE(
                SUM(preco * quantidade),
                0
            ) AS total
        FROM produtos
    """).fetchone()["total"]


    # ==============================
    # VALOR TOTAL DAS ENTRADAS
    # ==============================

    valor_entradas = conn.execute("""
        SELECT
            COALESCE(
                SUM(valor_total),
                0
            ) AS total
        FROM movimentacoes
        WHERE tipo = 'entrada'
          AND valor_total IS NOT NULL
    """).fetchone()["total"]


    # ==============================
    # VALOR TOTAL DAS SAÍDAS
    # ==============================

    valor_saidas = conn.execute("""
        SELECT
            COALESCE(
                SUM(valor_total),
                0
            ) AS total
        FROM movimentacoes
        WHERE tipo = 'saida'
          AND valor_total IS NOT NULL
    """).fetchone()["total"]


    conn.close()


    return jsonify({
        "valor_estoque":
            round(float(valor_estoque or 0), 2),

        "valor_entradas":
            round(float(valor_entradas or 0), 2),

        "valor_saidas":
            round(float(valor_saidas or 0), 2)
    }), 200
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

    # ==============================
    # ARQUIVAMENTO MENSAL AUTOMÁTICO
    # ==============================

    if usuario["perfil"] == "Administrador":

        try:

            resultado_arquivamento = (
                arquivar_relatorio_mes_anterior()
            )

            if resultado_arquivamento["gerado"]:

                print(
                    "Relatório mensal arquivado "
                    "automaticamente:",
                    resultado_arquivamento["caminho"]
                )

        except Exception as erro:

            # Um problema na geração do relatório
            # não deve impedir o administrador
            # de entrar no sistema.

            print(
                "Erro no arquivamento mensal "
                "automático:",
                erro
            )

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
# ==============================
# MIGRAR RELATÓRIOS ANTIGOS
# ==============================

def migrar_relatorios_antigos():

    nomes_meses = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro"
    }


    # ==============================
    # PASTA PRINCIPAL
    # ==============================

    pasta_relatorios = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "relatorios"
    )


    if not os.path.isdir(
        pasta_relatorios
    ):
        return


    conn = conectar_banco()


    try:

        # ==============================
        # PERCORRER ANOS
        # ==============================

        for nome_ano in os.listdir(
            pasta_relatorios
        ):

            caminho_ano = os.path.join(
                pasta_relatorios,
                nome_ano
            )


            if not os.path.isdir(
                caminho_ano
            ):
                continue


            try:

                ano = int(
                    nome_ano
                )

            except ValueError:

                continue


            # ==========================
            # PERCORRER MESES
            # ==========================

            for nome_pasta_mes in os.listdir(
                caminho_ano
            ):

                caminho_mes = os.path.join(
                    caminho_ano,
                    nome_pasta_mes
                )


                if not os.path.isdir(
                    caminho_mes
                ):
                    continue


                try:

                    mes = int(
                        nome_pasta_mes.split(
                            "-",
                            1
                        )[0]
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    continue


                if mes not in nomes_meses:
                    continue


                # ======================
                # PROCURAR PDFs
                # ======================

                for nome_arquivo in os.listdir(
                    caminho_mes
                ):

                    if not nome_arquivo.lower().endswith(
                        ".pdf"
                    ):
                        continue


                    caminho_arquivo = os.path.join(
                        caminho_mes,
                        nome_arquivo
                    )


                    if not os.path.isfile(
                        caminho_arquivo
                    ):
                        continue


                    # ==================
                    # DATA DO ARQUIVO
                    # ==================

                    timestamp = os.path.getmtime(
                        caminho_arquivo
                    )


                    data_geracao = (
                        datetime.fromtimestamp(
                            timestamp
                        ).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )


                    # ==================
                    # REGISTRAR NO BANCO
                    # ==================

                    conn.execute("""
                        INSERT OR IGNORE INTO
                        relatorios_arquivados (
                            ano,
                            mes,
                            nome_arquivo,
                            caminho_arquivo,
                            tipo_geracao,
                            data_geracao,
                            usuario_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ano,
                        mes,
                        nome_arquivo,
                        caminho_arquivo,
                        "manual",
                        data_geracao,
                        None
                    ))


        # ==============================
        # SALVAR ALTERAÇÕES
        # ==============================

        conn.commit()


    finally:

        conn.close()


# ==============================
# INICIAR APLICAÇÃO
# ==============================

if __name__ == "__main__":

    inicializar_banco()

    migrar_relatorios_antigos()

    app.run(
        debug=True
    )