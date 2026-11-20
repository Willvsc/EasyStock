"""Análises determinísticas, somente leitura, sobre o estoque do EasyStock."""
from datetime import datetime, timedelta
import math

LIMITE = 15

def _brl(n):
    return 'R$ ' + f'{n:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def _base(conn, dias=30):
    inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
    return conn.execute('''
        SELECT p.id, p.nome, p.sku, p.quantidade, p.preco,
               COALESCE(c.nome,'Sem categoria') AS categoria,
               COALESCE(SUM(CASE WHEN LOWER(m.tipo)='saida' AND m.data_hora>=? THEN m.quantidade ELSE 0 END),0) AS saidas,
               COALESCE(SUM(CASE WHEN LOWER(m.tipo)='entrada' AND m.data_hora>=? THEN m.quantidade ELSE 0 END),0) AS entradas,
               COUNT(CASE WHEN LOWER(m.tipo)='saida' AND m.data_hora>=? THEN 1 END) AS operacoes_saida
        FROM produtos p LEFT JOIN categorias c ON c.id=p.categoria_id
        LEFT JOIN movimentacoes m ON m.produto_id=p.id
        GROUP BY p.id ORDER BY p.nome COLLATE NOCASE
    ''',(inicio,inicio,inicio)).fetchall()

def analisar(conn, intent, dias=30, termo='', cobertura=14):
    dias = max(1,min(365,int(dias)))
    cobertura = max(1,min(90,int(cobertura)))
    rows = list(_base(conn,dias))
    if termo:
        from .assistant import _normalizar
        t=_normalizar(termo)
        rows=[r for r in rows if t in _normalizar(r['nome']) or t in _normalizar(r['sku'])]
    if not rows: return 'Nenhum produto encontrado para esta análise.'
    if intent=='zerados':
        dados=[r for r in rows if r['quantidade']==0]
        return ('Produtos sem estoque: '+str(len(dados))+'\n'+'\n'.join(f"• {r['nome']} (SKU {r['sku']})" for r in dados[:LIMITE])) if dados else 'Nenhum produto sem estoque.'
    if intent=='valor':
        valor=sum(r['quantidade']*r['preco'] for r in rows)
        return f'Valor estimado do estoque (preço cadastrado × quantidade): {_brl(valor)}. São {sum(r["quantidade"] for r in rows)} unidades em {len(rows)} produtos. Não representa lucro ou custo de aquisição.'
    if intent=='consumo':
        total=sum(r['saidas'] for r in rows)
        dados=sorted([r for r in rows if r['saidas']>0],key=lambda r:(-r['saidas'],r['nome']))
        cab=f'Consumo registrado nos últimos {dias} dias: {total} unidades em saídas; média geral de {total/dias:.2f} un./dia.\n'
        return cab + ('\n'.join(f"• {r['nome']} ({r['sku']}): {r['saidas']} saídas em unidades; média {r['saidas']/dias:.2f} un./dia." for r in dados[:LIMITE]) if dados else 'Sem saídas registradas no período.')
    if intent=='ranking':
        dados=sorted([r for r in rows if r['saidas']>0],key=lambda r:(-r['saidas'],r['nome']))
        return f'Produtos com mais saídas nos últimos {dias} dias:\n' + ('\n'.join(f"{i}. {r['nome']} ({r['sku']}): {r['saidas']} un." for i,r in enumerate(dados[:LIMITE],1)) if dados else 'Não há saídas registradas no período.')
    if intent=='parados':
        dados=[r for r in rows if r['saidas']==0 and r['quantidade']>0]
        return f'Produtos com estoque e nenhuma saída registrada nos últimos {dias} dias ({len(dados)}):\n' + ('\n'.join(f"• {r['nome']} ({r['sku']}): {r['quantidade']} un." for r in dados[:LIMITE]) if dados else 'Nenhum produto com estoque sem saídas no período.') + '\nA ausência de saídas no período não prova que o produto nunca vendeu.'
    if intent=='cobertura':
        linhas=[]
        for r in rows:
            if r['saidas']:
                media=r['saidas']/dias
                linhas.append((r['quantidade']/media,r,media))
        linhas.sort(key=lambda x:x[0])
        return f'Cobertura estimada com base nas saídas dos últimos {dias} dias:\n' + ('\n'.join(f"• {r['nome']} ({r['sku']}): {c:.1f} dia(s) de cobertura; {r['quantidade']} un. disponíveis." for c,r,_ in linhas[:LIMITE]) if linhas else 'Sem histórico de saídas suficiente para calcular cobertura.') + '\nEstimativa baseada na média histórica, não previsão garantida.'
    if intent=='reposicao':
        propostas=[]; sem_historico=[]
        for r in rows:
            media=r['saidas']/dias
            if media>0:
                alvo=math.ceil(media*cobertura)
                comprar=max(0,alvo-r['quantidade'])
                if comprar: propostas.append((r['quantidade']/media,r,comprar,media))
            elif r['quantidade']<=5:
                sem_historico.append(r)
        propostas.sort(key=lambda x:(x[0],-x[2]))
        partes=[f'Recomendações de reposição (histórico: {dias} dias; cobertura-alvo: {cobertura} dias).']
        if propostas:
            partes.extend(f"• {r['nome']} ({r['sku']}): estoque {r['quantidade']} un.; consumo {media:.2f} un./dia; cobertura {c:.1f} dia(s); sugerido comprar {q} un." for c,r,q,media in propostas[:LIMITE])
        else: partes.append('Nenhum produto com consumo registrado precisa de reposição para a cobertura escolhida.')
        if sem_historico:
            partes.append('Atenção: sem saídas no período e estoque baixo/zerado (não há base para calcular compra):')
            partes.extend(f"• {r['nome']} ({r['sku']}): {r['quantidade']} un." for r in sem_historico[:LIMITE])
        partes.append('Sugestões informativas: revise sazonalidade, prazo de fornecedor e pedidos pendentes antes de comprar. Nenhuma compra é executada.')
        return '\n'.join(partes)
    return 'Análise não reconhecida.'
