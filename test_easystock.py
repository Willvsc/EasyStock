import os
import tempfile
import unittest

import main
from main import app


# ============================================================
# TESTES DE AUTENTICAÇÃO, PERMISSÕES E VALIDAÇÕES
# ============================================================

class TestEasyStock(unittest.TestCase):

    def setUp(self):

        app.config["TESTING"] = True

        self.client = app.test_client()


    # ========================================================
    # TESTE 01
    # LOGIN COM CREDENCIAIS INVÁLIDAS
    # ========================================================

    def test_login_invalido(self):

        resposta = self.client.post(
            "/api/login",
            json={
                "email": "usuario_inexistente@teste.com",
                "senha": "senha_incorreta"
            }
        )

        self.assertEqual(
            resposta.status_code,
            401
        )

        dados = resposta.get_json()

        self.assertEqual(
            dados["erro"],
            "E-mail ou senha inválidos."
        )


    # ========================================================
    # TESTE 02
    # LOGIN COM CAMPOS VAZIOS
    # ========================================================

    def test_login_campos_vazios(self):

        resposta = self.client.post(
            "/api/login",
            json={
                "email": "",
                "senha": ""
            }
        )

        self.assertEqual(
            resposta.status_code,
            400
        )

        dados = resposta.get_json()

        self.assertEqual(
            dados["erro"],
            "E-mail e senha são obrigatórios."
        )


    # ========================================================
    # TESTE 03
    # HISTÓRICO SEM AUTENTICAÇÃO
    # ========================================================

    def test_movimentacoes_sem_autenticacao(self):

        resposta = self.client.get(
            "/api/movimentacoes"
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 04
    # RELATÓRIOS ARQUIVADOS SEM AUTENTICAÇÃO
    # ========================================================

    def test_relatorios_sem_autenticacao(self):

        resposta = self.client.get(
            "/api/relatorios/arquivados"
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 05
    # CADASTRO DE PRODUTO SEM AUTENTICAÇÃO
    # ========================================================

    def test_cadastrar_produto_sem_autenticacao(self):

        resposta = self.client.post(
            "/api/produtos",
            json={
                "nome": "Produto Teste",
                "categoria": "Alimentos",
                "preco": 10.00,
                "quantidade": 5,
                "sku": "TESTE-AUTO"
            }
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 06
    # ALTERAÇÃO DE ESTOQUE SEM AUTENTICAÇÃO
    # ========================================================

    def test_alterar_estoque_sem_autenticacao(self):

        resposta = self.client.patch(
            "/api/produtos/1/quantidade",
            json={
                "operacao": "adicionar",
                "quantidade": 1
            }
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 07
    # EXCLUSÃO DE PRODUTO SEM AUTENTICAÇÃO
    # ========================================================

    def test_excluir_produto_sem_autenticacao(self):

        resposta = self.client.delete(
            "/api/produtos/1"
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 08
    # CADASTRO DE CATEGORIA SEM AUTENTICAÇÃO
    # ========================================================

    def test_cadastrar_categoria_sem_autenticacao(self):

        resposta = self.client.post(
            "/api/categorias",
            json={
                "nome": "Categoria Teste"
            }
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 09
    # RELATÓRIO MENSAL SEM AUTENTICAÇÃO
    # ========================================================

    def test_relatorio_mensal_sem_autenticacao(self):

        resposta = self.client.get(
            "/api/relatorios/movimentacoes",
            query_string={
                "mes": 9,
                "ano": 2026
            }
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 10
    # PDF DO RELATÓRIO SEM AUTENTICAÇÃO
    # ========================================================

    def test_pdf_relatorio_sem_autenticacao(self):

        resposta = self.client.get(
            "/api/relatorios/movimentacoes/pdf",
            query_string={
                "mes": 9,
                "ano": 2026
            }
        )

        self.assertEqual(
            resposta.status_code,
            401
        )


    # ========================================================
    # TESTE 11
    # FUNCIONÁRIO NÃO PODE CADASTRAR PRODUTO
    # ========================================================

    def test_funcionario_nao_pode_cadastrar_produto(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Funcionário"

        resposta = self.client.post(
            "/api/produtos",
            json={
                "nome": "Produto Teste",
                "categoria": "Teste",
                "preco": 10,
                "quantidade": 5,
                "sku": "AUTO-001"
            }
        )

        self.assertEqual(
            resposta.status_code,
            403
        )


    # ========================================================
    # TESTE 12
    # FUNCIONÁRIO NÃO PODE EXCLUIR PRODUTO
    # ========================================================

    def test_funcionario_nao_pode_excluir_produto(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Funcionário"

        resposta = self.client.delete(
            "/api/produtos/1"
        )

        self.assertEqual(
            resposta.status_code,
            403
        )


    # ========================================================
    # TESTE 13
    # FUNCIONÁRIO NÃO PODE CADASTRAR CATEGORIA
    # ========================================================

    def test_funcionario_nao_pode_cadastrar_categoria(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Funcionário"

        resposta = self.client.post(
            "/api/categorias",
            json={
                "nome": "Categoria Automática"
            }
        )

        self.assertEqual(
            resposta.status_code,
            403
        )


    # ========================================================
    # TESTE 14
    # GERENTE NÃO PODE ACESSAR USUÁRIOS
    # ========================================================

    def test_gerente_nao_pode_acessar_usuarios(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Gerente"

        resposta = self.client.get(
            "/api/usuarios"
        )

        self.assertEqual(
            resposta.status_code,
            403
        )


    # ========================================================
    # TESTE 15
    # FUNCIONÁRIO NÃO PODE ACESSAR USUÁRIOS
    # ========================================================

    def test_funcionario_nao_pode_acessar_usuarios(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Funcionário"

        resposta = self.client.get(
            "/api/usuarios"
        )

        self.assertEqual(
            resposta.status_code,
            403
        )


    # ========================================================
    # TESTE 16
    # PRODUTO COM CAMPOS OBRIGATÓRIOS VAZIOS
    # ========================================================

    def test_produto_campos_obrigatorios_vazios(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Administrador"

        resposta = self.client.post(
            "/api/produtos",
            json={
                "nome": "",
                "categoria": "",
                "preco": 10,
                "quantidade": 5,
                "sku": ""
            }
        )

        self.assertEqual(
            resposta.status_code,
            400
        )

        dados = resposta.get_json()

        self.assertEqual(
            dados["erro"],
            "Preencha todos os campos obrigatórios."
        )


    # ========================================================
    # TESTE 17
    # PRODUTO COM PREÇO INVÁLIDO
    # ========================================================

    def test_produto_preco_invalido(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Administrador"

        resposta = self.client.post(
            "/api/produtos",
            json={
                "nome": "Produto Teste",
                "categoria": "Teste",
                "preco": 0,
                "quantidade": 5,
                "sku": "AUTO-002"
            }
        )

        self.assertEqual(
            resposta.status_code,
            400
        )

        dados = resposta.get_json()

        self.assertEqual(
            dados["erro"],
            "O preço deve ser maior que zero."
        )


    # ========================================================
    # TESTE 18
    # PRODUTO COM QUANTIDADE NEGATIVA
    # ========================================================

    def test_produto_quantidade_negativa(self):

        with self.client.session_transaction() as sess:
            sess["usuario_id"] = 999
            sess["perfil"] = "Administrador"

        resposta = self.client.post(
            "/api/produtos",
            json={
                "nome": "Produto Teste",
                "categoria": "Teste",
                "preco": 10,
                "quantidade": -1,
                "sku": "AUTO-003"
            }
        )

        self.assertEqual(
            resposta.status_code,
            400
        )

        dados = resposta.get_json()

        self.assertEqual(
            dados["erro"],
            "A quantidade não pode ser negativa."
        )


# ============================================================
# TESTES DE INTEGRIDADE COM BANCO TEMPORÁRIO
# ============================================================

class TestEasyStockIntegridade(unittest.TestCase):

    def setUp(self):

        # ====================================================
        # CRIAR BANCO TEMPORÁRIO
        # ====================================================

        arquivo_temporario = tempfile.NamedTemporaryFile(
            suffix=".db",
            delete=False
        )

        self.banco_teste = arquivo_temporario.name

        arquivo_temporario.close()


        # ====================================================
        # GUARDAR BANCO ORIGINAL
        # ====================================================

        self.banco_original = main.DATABASE


        # ====================================================
        # APONTAR A APLICAÇÃO PARA O BANCO TEMPORÁRIO
        # ====================================================

        main.DATABASE = self.banco_teste


        # ====================================================
        # CRIAR AS TABELAS
        # ====================================================

        main.inicializar_banco()


        # ====================================================
        # CONFIGURAR CLIENTE FLASK
        # ====================================================

        app.config["TESTING"] = True

        self.client = app.test_client()


        # ====================================================
        # PREPARAR DADOS
        # ====================================================

        conn = main.conectar_banco()


        # ----------------------------------------------------
        # Categoria de teste
        # ----------------------------------------------------

        conn.execute("""
            INSERT OR IGNORE INTO categorias (nome)
            VALUES (?)
        """, (
            "Categoria Teste",
        ))


        # ----------------------------------------------------
        # Localizar perfil Administrador
        # ----------------------------------------------------

        perfil = conn.execute("""
            SELECT id
            FROM perfil
            WHERE nome = ?
        """, (
            "Administrador",
        )).fetchone()


        self.assertIsNotNone(
            perfil,
            "Perfil Administrador não foi criado no banco de teste."
        )


        # ----------------------------------------------------
        # Criar usuário de teste
        # ----------------------------------------------------

        cursor = conn.execute("""
            INSERT INTO usuario (
                nome,
                email,
                senha,
                perfil_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            "Administrador Teste",
            "admin.teste@easystock.local",
            "senha_teste",
            perfil["id"]
        ))


        self.usuario_id = cursor.lastrowid


        # ----------------------------------------------------
        # Criar produto inicial
        #
        # Quantidade inicial = 10
        # ----------------------------------------------------

        cursor = conn.execute("""
            INSERT INTO produtos (
                nome,
                categoria_id,
                preco,
                quantidade,
                sku
            )
            SELECT
                ?,
                id,
                ?,
                ?,
                ?
            FROM categorias
            WHERE nome = ?
        """, (
            "Produto Automatizado",
            10.00,
            10,
            "AUTO-INTEGRIDADE",
            "Categoria Teste"
        ))


        self.produto_id = cursor.lastrowid


        conn.commit()
        conn.close()


        # ====================================================
        # CRIAR SESSÃO DE ADMINISTRADOR
        # ====================================================

        with self.client.session_transaction() as sess:

            sess["usuario_id"] = self.usuario_id
            sess["perfil"] = "Administrador"


    def tearDown(self):

        # ====================================================
        # RESTAURAR BANCO REAL
        # ====================================================

        main.DATABASE = self.banco_original


        # ====================================================
        # EXCLUIR BANCO TEMPORÁRIO
        # ====================================================

        if os.path.exists(self.banco_teste):

            try:

                os.remove(
                    self.banco_teste
                )

            except PermissionError:

                pass


    # ========================================================
    # TESTE 19
    # SKU DUPLICADO
    # ========================================================

    def test_sku_duplicado(self):

        resposta = self.client.post(
            "/api/produtos",
            json={
                "nome": "Outro Produto",
                "categoria": "Categoria Teste",
                "preco": 20,
                "quantidade": 5,
                "sku": "AUTO-INTEGRIDADE"
            }
        )


        self.assertEqual(
            resposta.status_code,
            400
        )


        dados = resposta.get_json()


        self.assertEqual(
            dados["erro"],
            "Já existe um produto com esse SKU."
        )


    # ========================================================
    # TESTE 20
    # SAÍDA MAIOR QUE O ESTOQUE
    # ========================================================

    def test_saida_maior_que_estoque(self):

        resposta = self.client.patch(
            f"/api/produtos/{self.produto_id}/quantidade",
            json={
                "operacao": "remover",
                "quantidade": 20
            }
        )


        self.assertEqual(
            resposta.status_code,
            400
        )


        # ----------------------------------------------------
        # Confirmar que o estoque continua 10
        # ----------------------------------------------------

        conn = main.conectar_banco()


        produto = conn.execute("""
            SELECT quantidade
            FROM produtos
            WHERE id = ?
        """, (
            self.produto_id,
        )).fetchone()


        conn.close()


        self.assertEqual(
            produto["quantidade"],
            10
        )


    # ========================================================
    # TESTE 21
    # ENTRADA ATUALIZA O ESTOQUE
    # ========================================================

    def test_entrada_atualiza_estoque(self):

        resposta = self.client.patch(
            f"/api/produtos/{self.produto_id}/quantidade",
            json={
                "operacao": "adicionar",
                "quantidade": 5
            }
        )


        self.assertEqual(
            resposta.status_code,
            200
        )


        dados = resposta.get_json()


        self.assertEqual(
            dados["quantidade"],
            15
        )


        # ----------------------------------------------------
        # Confirmar diretamente no banco
        # ----------------------------------------------------

        conn = main.conectar_banco()


        produto = conn.execute("""
            SELECT quantidade
            FROM produtos
            WHERE id = ?
        """, (
            self.produto_id,
        )).fetchone()


        conn.close()


        self.assertEqual(
            produto["quantidade"],
            15
        )


    # ========================================================
    # TESTE 22
    # SAÍDA ATUALIZA O ESTOQUE
    # ========================================================

    def test_saida_atualiza_estoque(self):

        resposta = self.client.patch(
            f"/api/produtos/{self.produto_id}/quantidade",
            json={
                "operacao": "remover",
                "quantidade": 3
            }
        )


        self.assertEqual(
            resposta.status_code,
            200
        )


        dados = resposta.get_json()


        self.assertEqual(
            dados["quantidade"],
            7
        )


        # ----------------------------------------------------
        # Confirmar diretamente no banco
        # ----------------------------------------------------

        conn = main.conectar_banco()


        produto = conn.execute("""
            SELECT quantidade
            FROM produtos
            WHERE id = ?
        """, (
            self.produto_id,
        )).fetchone()


        conn.close()


        self.assertEqual(
            produto["quantidade"],
            7
        )


    # ========================================================
    # TESTE 23
    # ENTRADA GERA MOVIMENTAÇÃO
    # ========================================================

    def test_entrada_gera_movimentacao(self):

        resposta = self.client.patch(
            f"/api/produtos/{self.produto_id}/quantidade",
            json={
                "operacao": "adicionar",
                "quantidade": 4
            }
        )


        self.assertEqual(
            resposta.status_code,
            200
        )


        conn = main.conectar_banco()


        movimentacao = conn.execute("""
            SELECT
                produto_id,
                tipo,
                quantidade,
                usuario_id
            FROM movimentacoes
            WHERE produto_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (
            self.produto_id,
        )).fetchone()


        conn.close()


        self.assertIsNotNone(
            movimentacao
        )


        self.assertEqual(
            movimentacao["produto_id"],
            self.produto_id
        )


        self.assertEqual(
            movimentacao["tipo"],
            "entrada"
        )


        self.assertEqual(
            movimentacao["quantidade"],
            4
        )


        self.assertEqual(
            movimentacao["usuario_id"],
            self.usuario_id
        )


    # ========================================================
    # TESTE 24
    # SAÍDA GERA MOVIMENTAÇÃO
    # ========================================================

    def test_saida_gera_movimentacao(self):

        resposta = self.client.patch(
            f"/api/produtos/{self.produto_id}/quantidade",
            json={
                "operacao": "remover",
                "quantidade": 2
            }
        )


        self.assertEqual(
            resposta.status_code,
            200
        )


        conn = main.conectar_banco()


        movimentacao = conn.execute("""
            SELECT
                produto_id,
                tipo,
                quantidade,
                usuario_id
            FROM movimentacoes
            WHERE produto_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (
            self.produto_id,
        )).fetchone()


        conn.close()


        self.assertIsNotNone(
            movimentacao
        )


        self.assertEqual(
            movimentacao["produto_id"],
            self.produto_id
        )


        self.assertEqual(
            movimentacao["tipo"],
            "saida"
        )


        self.assertEqual(
            movimentacao["quantidade"],
            2
        )


        self.assertEqual(
            movimentacao["usuario_id"],
            self.usuario_id
        )


    # ========================================================
    # TESTE 25
    # INTEGRIDADE DO FLUXO COMPLETO
    # ========================================================

    def test_integridade_fluxo_movimentacoes(self):

        # ----------------------------------------------------
        # ESTOQUE INICIAL = 10
        #
        # Entrada +5
        # Saída   -2
        #
        # Resultado esperado = 13
        # ----------------------------------------------------


        # Entrada +5

        resposta_entrada = self.client.patch(
            f"/api/produtos/{self.produto_id}/quantidade",
            json={
                "operacao": "adicionar",
                "quantidade": 5
            }
        )


        self.assertEqual(
            resposta_entrada.status_code,
            200
        )


        # Saída -2

        resposta_saida = self.client.patch(
            f"/api/produtos/{self.produto_id}/quantidade",
            json={
                "operacao": "remover",
                "quantidade": 2
            }
        )


        self.assertEqual(
            resposta_saida.status_code,
            200
        )


        # ----------------------------------------------------
        # CONSULTAR RESULTADO NO BANCO
        # ----------------------------------------------------

        conn = main.conectar_banco()


        produto = conn.execute("""
            SELECT quantidade
            FROM produtos
            WHERE id = ?
        """, (
            self.produto_id,
        )).fetchone()


        movimentacoes = conn.execute("""
            SELECT
                tipo,
                quantidade
            FROM movimentacoes
            WHERE produto_id = ?
            ORDER BY id
        """, (
            self.produto_id,
        )).fetchall()


        conn.close()


        # ----------------------------------------------------
        # QUANTIDADE FINAL
        # 10 + 5 - 2 = 13
        # ----------------------------------------------------

        self.assertEqual(
            produto["quantidade"],
            13
        )


        # ----------------------------------------------------
        # DEVEM EXISTIR DUAS MOVIMENTAÇÕES
        # ----------------------------------------------------

        self.assertEqual(
            len(movimentacoes),
            2
        )


        # ----------------------------------------------------
        # PRIMEIRA MOVIMENTAÇÃO = ENTRADA DE 5
        # ----------------------------------------------------

        self.assertEqual(
            movimentacoes[0]["tipo"],
            "entrada"
        )


        self.assertEqual(
            movimentacoes[0]["quantidade"],
            5
        )


        # ----------------------------------------------------
        # SEGUNDA MOVIMENTAÇÃO = SAÍDA DE 2
        # ----------------------------------------------------

        self.assertEqual(
            movimentacoes[1]["tipo"],
            "saida"
        )


        self.assertEqual(
            movimentacoes[1]["quantidade"],
            2
        )


# ============================================================
# EXECUTAR TESTES
# ============================================================

if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )