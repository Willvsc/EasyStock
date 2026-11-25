"""Auditoria somente leitura do banco local."""
import sqlite3, sys
from pathlib import Path
p=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).with_name('estoque.db')).resolve()
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as c:
    c.execute('PRAGMA foreign_keys=ON')
    integrity=c.execute('PRAGMA integrity_check').fetchall()
    fk=c.execute('PRAGMA foreign_key_check').fetchall()
    print('Integridade:',integrity,'\nChaves estrangeiras:',fk)
    for t in ('perfil','usuario','categorias','produtos','movimentacoes','relatorios_arquivados'):
        print(t, c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
    invalid=c.execute('SELECT COUNT(*) FROM produtos WHERE preco<=0 OR quantidade<0').fetchone()[0]
    invalid+=c.execute("SELECT COUNT(*) FROM movimentacoes WHERE quantidade<=0 OR tipo NOT IN ('entrada','saida')").fetchone()[0]
    link=any(r[3]=='usuario_id' for r in c.execute('PRAGMA foreign_key_list(movimentacoes)'))
    print('Registros inválidos:',invalid,'\nFK movimentacoes.usuario_id:',link)
    ok=integrity==[('ok',)] and not fk and not invalid and link
    print('OK' if ok else 'REVISAR')
    sys.exit(0 if ok else 1)
