import tempfile, unittest, sqlite3
from pathlib import Path
import main

class TestRC1(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        old=main.DATABASE; self.addCleanup(setattr,main,'DATABASE',old)
        main.DATABASE=str(Path(self.tmp.name)/'test.db'); main.inicializar_banco()
        main.app.config['TESTING']=True; self.client=main.app.test_client()
    def test_schema(self):
        c=main.conectar_banco()
        try:
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
            self.assertTrue(any(r['from']=='usuario_id' for r in c.execute('PRAGMA foreign_key_list(movimentacoes)')))
        finally:c.close()
    def test_json_invalido(self):
        for payload in ([], {'email':123}, {'senha':None}):
            self.assertEqual(self.client.post('/api/login',json=payload).status_code,400)
    def test_rotas_protegidas(self):
        for route in ('/api/produtos','/api/categorias','/api/relatorios/movimentacoes/dados'):
            self.assertEqual(self.client.get(route).status_code,401)
    def test_ai_sem_sessao(self):
        self.assertEqual(self.client.post('/api/ai/chat',json={'mensagem':'estoque'}).status_code,401)
