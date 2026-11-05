# EasyStock AI — Sprint 08, Etapa 1

## Entregue no código
- Chatbot lateral reutilizado no `base.html` para páginas autenticadas.
- API `POST /api/ai/chat` exige sessão, JSON e mensagem de até 500 caracteres.
- Integração com API OpenAI configurada por variáveis de ambiente, sem chave no código.
- Classificação de perguntas pela IA; consultas SQLite com SQL fixo, parametrizado e somente leitura.
- Consultas de produtos (nome, SKU, preço, categoria, quantidade), movimentações (produto, tipo, período) e resumo de produtos/unidades.
- Limite de 15 registros por resposta; avisos quando resultados são truncados.
- Erros de configuração ou rede exibidos sem expor a chave.

## Como configurar
1. Instale as dependências já usadas pelo projeto e inicie o Flask como de costume.
2. No terminal PowerShell, antes de iniciar o servidor: `$env:OPENAI_API_KEY="SUA_CHAVE"`.
3. Opcional: `$env:EASYSTOCK_AI_MODEL="gpt-4.1-mini"` (modelo disponível na sua conta/API).
4. Faça login no EasyStock e abra o botão **EasyStock AI** no canto inferior direito.
5. Experimente: "Qual o preço do feijão?", "Quais são os produtos cadastrados?", "Mostre as saídas dos últimos 30 dias" e "Quantos itens temos no estoque?".

**Importante:** a assinatura ChatGPT não equivale a créditos de API; a API pode ser cobrada separadamente. Não compartilhe sua chave e não coloque a chave no JavaScript.

## Limitações da Etapa 1
- Chatbot somente leitura: NÃO cadastra, edita ou movimenta produtos.
- Respostas formatadas pelo backend com dados reais, não há geração de texto livre a partir dos registros.
- A conversa é mantida visualmente enquanto a página estiver aberta, sem memória persistente ou contexto entre perguntas.
- Análises preditivas, recomendações de reposição, ações administrativas com confirmação, trilha de auditoria das ações, Ollama e testes integrados com API real são etapas futuras.
- Não substitui a revisão de permissões e segurança antes do deploy.

## Plano registrado para as próximas etapas
**Etapa 2:** análises estatísticas, consumo médio, cobertura de estoque, recomendações e explicações.
**Etapa 3:** entradas e saídas, cadastro e edição pelo chatbot; prévia e confirmação obrigatória; mesma lógica de negócio da interface; checagem de perfil e auditoria de usuário/origem/resultado.
**Etapa 4:** testes de integração, acessos negados, duplicidade de confirmação, consistência de estoque e documentação de evidências.
**Posteriormente:** provedor Ollama intercambiável e novas ferramentas para futuros módulos.

## Relação com os requisitos da Sprint 08
A Etapa 1 demonstra evolução prática do componente tecnológico. Entretanto, a entrega acadêmica também exige revisão das regras de negócio, permissões, melhorias de usabilidade, funcionalidades completas do escopo e PDF cumulativo das Sprints 01–08. Essas evidências devem ser obtidas e documentadas separadamente; não devem ser declaradas como concluídas sem teste.
