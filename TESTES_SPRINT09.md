# EasyStock — Sprint 09 | Correção 01

Turma: 8NA

## Arquivos modificados
- `main.py`: exige sessão autenticada em `GET /api/produtos` e `GET /api/categorias` (HTTP 401 quando não autenticado).
- `easystock_ai/assistant.py`: usa estoque baixo de 1 a 5 unidades, em concordância com `GET /api/analise/indicadores`. Estoque zero é tratado separadamente como sem estoque.

## Instalação
1. Faça backup do projeto e do arquivo `estoque.db`.
2. Pare o Flask.
3. Copie os dois arquivos deste patch para a raiz do projeto, respeitando a subpasta `easystock_ai/`.
4. Execute `python -m unittest test_easystock -v` e `python main.py`.
5. Verifique os casos abaixo e registre prints/resultados reais.

## Casos de teste para executar
- CT09-01: sem login, `GET /api/produtos` -> HTTP 401, JSON `Usuário não autenticado.`
- CT09-02: sem login, `GET /api/categorias` -> HTTP 401, JSON `Usuário não autenticado.`
- CT09-03: autenticado, telas Produtos e Categorias continuam carregando corretamente.
- CT09-04: EasyStock AI local: produto com 0 unidades NÃO aparece em estoque baixo; deve aparecer como sem estoque nos indicadores.
- CT09-05: EasyStock AI local: produtos com 1 e 5 unidades aparecem em estoque baixo; produto com 6 não aparece.
- CT09-06: confirmar que Dashboard e análise do estoque exibem contagens coerentes.
- CT09-07: executar regressão de cadastro, edição, movimentações, relatórios e permissões por perfil.

## Limites e pendências
- Esta correção exige autenticação para as listagens; não redefine quais perfis autenticados podem consultar os dados.
- O Dashboard e outras telas podem usar indicadores com critérios próprios; fazer auditoria de ponta a ponta.
- A suíte de testes não pôde ser executada no ambiente de preparação porque o pacote Flask não estava disponível. Apenas a sintaxe dos arquivos modificados foi verificada.
- Nenhuma funcionalidade de análise avançada do EasyStock AI foi implementada neste patch.
