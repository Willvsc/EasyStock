# API EasyStock — RC1
Base: `http://127.0.0.1:5000`. JSON UTF-8. A autenticação usa cookie de sessão Flask obtido no login; envie o cookie nas demais chamadas. A = Administrador; G = Gerente; F = Funcionário. As rotas protegidas retornam 401 sem sessão e 403 quando o perfil não permite a operação. Erros de validação retornam normalmente 400 com `{"erro":"..."}`; recursos inexistentes podem retornar 404; falha interna 500; indisponibilidade da IA 503. Cadastros bem-sucedidos retornam 201 ou 200 conforme a rota; consultas e alterações bem-sucedidas retornam 200.

| Método | Rota | Perfil | Entrada | Resposta de sucesso |
|---|---|---|---|---|
| POST | /api/login | Público | email, senha | mensagem, usuario e cookie |
| POST | /api/logout | Todos | — | mensagem, sessão encerrada |
| GET | /api/sessao | A/G/F | — | autenticado, usuario |
| GET | /api/produtos | A/G/F | — | lista: id, nome, preco, quantidade, sku, categoria_id, categoria |
| POST | /api/produtos | A/G | nome, categoria (nome), preco, quantidade, sku | confirmação |
| PUT | /api/produtos/{produto_id} | A/G | nome, categoria, preco, sku | confirmação |
| DELETE | /api/produtos/{produto_id} | A/G | ID na rota | confirmação |
| PATCH | /api/produtos/{produto_id}/quantidade | A/G/F | operacao: adicionar/remover; quantidade (padrão 1) | confirmação e atualização do estoque |
| GET | /api/categorias | A/G/F | — | lista: id, nome, quantidade_produtos |
| POST | /api/categorias | A/G | nome | confirmação |
| PUT | /api/categorias/{categoria_id} | A/G | nome | confirmação |
| DELETE | /api/categorias/{categoria_id} | A/G | ID na rota | confirmação |
| GET | /api/movimentacoes | A/G/F | — | histórico de entradas/saídas, data, produto, usuário e valores |
| GET | /api/analise/indicadores | A | — | indicadores de estoque |
| GET | /api/analise/movimentacoes | A | mes e ano opcionais juntos | resumo de movimentações |
| GET | /api/analise/produtos-mais-movimentados | A | mes e ano opcionais juntos | ranking |
| GET | /api/dashboard/financeiro | A | — | indicadores financeiros |
| GET | /api/relatorios/movimentacoes | A | mes, ano | PDF (rota legada) |
| GET | /api/relatorios/movimentacoes/pdf | A | mes, ano | PDF |
| GET | /api/relatorios/movimentacoes/dados | A | mes, ano | relatório JSON, resumo e movimentacoes |
| GET | /api/relatorios/arquivados | A | — | lista de relatórios |
| GET | /api/relatorios/arquivados/{ano}/{mes}/{nome_arquivo} | A | parâmetros de rota | PDF arquivado |
| GET | /api/usuarios | A | — | lista de usuários |
| POST | /api/usuarios | A | nome, email, senha, perfil_id | confirmação |
| PUT | /api/usuarios/{usuario_id} | A | nome, email, perfil_id | confirmação |
| DELETE | /api/usuarios/{usuario_id} | A | ID na rota | confirmação |
| GET | /api/perfis | A | — | lista de perfis |
| POST | /api/ai/chat | A/G/F | mensagem (1–500 caracteres), modo local/openai | resposta, modo, somente_leitura |

## Exemplos PowerShell
```powershell
$base = 'http://127.0.0.1:5000'
$cred = @{email='admin@easystock.com'; senha=(Read-Host 'Senha')} | ConvertTo-Json
Invoke-RestMethod "$base/api/login" -Method Post -ContentType 'application/json' -Body $cred -SessionVariable sess
Invoke-RestMethod "$base/api/produtos" -WebSession $sess
Invoke-RestMethod "$base/api/ai/chat" -Method Post -WebSession $sess -ContentType 'application/json' -Body '{"mensagem":"oq preciso repor?","modo":"local"}'
Invoke-RestMethod "$base/api/relatorios/movimentacoes/pdf?mes=11&ano=2026" -WebSession $sess -OutFile relatorio.pdf
```
SKU único, preço positivo, quantidade inteira não negativa, saída limitada ao saldo. A categoria deve existir. A exclusão de produto preserva histórico. CSV é exportado na interface. A documentação não afirma que o modo Cloud foi homologado.
