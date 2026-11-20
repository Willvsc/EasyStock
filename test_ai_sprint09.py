import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from easystock_ai.assistant import responder, interpretar_local

class TestAISprint09(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=Path(self.temp.name)/'test.db'
        c=sqlite3.connect(self.db)
        c.executescript('''CREATE TABLE categorias(id INTEGER PRIMARY KEY,nome TEXT);
        CREATE TABLE produtos(id INTEGER PRIMARY KEY,nome TEXT,sku TEXT,quantidade INTEGER,preco REAL,categoria_id INTEGER);
        CREATE TABLE movimentacoes(id INTEGER PRIMARY KEY,produto_id INTEGER,produto_nome TEXT,tipo TEXT,quantidade INTEGER,data_hora TEXT);
        INSERT INTO categorias VALUES(1,'Alimentos');
        INSERT INTO produtos VALUES(1,'Arroz','ARZ1',4,10,1),(2,'Milho','MLH1',0,5,1),(3,'Feijão','FEJ1',20,8,1);
        ''')
        hoje=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.executemany('INSERT INTO movimentacoes(produto_id,produto_nome,tipo,quantidade,data_hora) VALUES(?,?,?,?,?)',[(1,'Arroz','saida',30,hoje),(3,'Feijão','saida',2,hoje),(1,'Arroz','entrada',10,hoje)])
        c.commit();c.close()
    def tearDown(self):self.temp.cleanup()
    def conectar(self):
        c=sqlite3.connect(self.db);c.row_factory=sqlite3.Row;return c
    def perguntar(self,p):return responder(p,self.conectar)
    def test_reposicao(self):
        t=self.perguntar('oq preciso repor?');self.assertIn('Arroz',t);self.assertIn('10 un.',t)
    def test_reposicao_sem_acento(self):self.assertIn('Arroz',self.perguntar('recomendacoes de reposicao'))
    def test_abreviacoes(self):self.assertIn('4 un.',self.perguntar('qtd do arroz'))
    def test_baixo(self):self.assertIn('Arroz',self.perguntar('estoque baixo'));self.assertNotIn('Milho',self.perguntar('estoque baixo'))
    def test_zerados(self):self.assertIn('Milho',self.perguntar('sem estoque'))
    def test_valor(self):self.assertIn('R$ 200,00',self.perguntar('valor total do estoque'))
    def test_consumo(self):self.assertIn('32 unidades',self.perguntar('consumo medio'))
    def test_ranking(self):self.assertIn('Arroz',self.perguntar('mais vendidos'))
    def test_parados(self):self.assertNotIn('Arroz',self.perguntar('produtos parados'))
    def test_cobertura(self):self.assertIn('Arroz',self.perguntar('quantos dias dura o estoque'))
    def test_historico(self):self.assertIn('saida',self.perguntar('historico de saidas 7 dias'))
    def test_bloqueio_escrita(self):
        self.assertIn('Não cadastro',self.perguntar('excluir produto Arroz'))
        with closing(self.conectar()) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0], 3)
    def test_nao_cria_movimentacao(self):
        self.perguntar('o que preciso comprar')
        with closing(self.conectar()) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM movimentacoes').fetchone()[0], 3)
    def test_intencoes(self):
        for pergunta,esperado in [('ranking de saidas','ranking'),('estq baixo','baixo'),('cat','categorias'),('mov 7d','historico'),('repor','reposicao')]:
            with self.subTest(pergunta=pergunta):self.assertEqual(interpretar_local(pergunta)[0],esperado)

if __name__=='__main__':unittest.main()
