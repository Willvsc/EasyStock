# EasyStock — Release Candidate 1 (Sprint 10)

Sistema web de gestão de estoque para pequenos estabelecimentos. Centraliza produtos, categorias, movimentações, histórico, indicadores, relatórios PDF/CSV e usuários. O EasyStock AI Local interpreta consultas e calcula consumo, cobertura, ranking e recomendações de reposição, sem alterar o banco.

## Tecnologias e requisitos
Python 3.11 ou superior, Flask, SQLite, ReportLab, HTML, CSS e JavaScript. Navegador moderno. Git é opcional para execução. Internet necessária para instalar dependências e para o modo OpenAI Cloud opcional.

## Instalação no Windows (PowerShell)
Na pasta extraída, execute:
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```
Abra http://127.0.0.1:5000. O servidor é local, sem debug. O banco `estoque.db` é criado automaticamente se não existir. Em banco novo, o administrador `admin@easystock.com` recebe uma senha aleatória exibida uma única vez no terminal; alternativamente defina `$env:EASYSTOCK_ADMIN_PASSWORD` antes da primeira execução. Bancos existentes preservam suas contas e senhas. Não publique o banco nem senhas. Faça backup antes de iniciar uma atualização.

Variáveis opcionais: `SECRET_KEY` (segredo forte para manter sessões entre reinícios; sem ele é gerado um segredo por processo), `EASYSTOCK_DATABASE` (caminho do SQLite), `OPENAI_API_KEY` e `EASYSTOCK_AI_MODEL` (modo Cloud). Não versionar segredos. O modo Cloud depende de créditos e ainda precisa de validação ponta a ponta.

## Banco e testes
`database/schema.sql` documenta a estrutura de instalação nova; `main.py` inicializa e migra bancos existentes. Execute `python verificar_banco.py` para auditar integridade e relacionamentos. Execute `python -m unittest test_easystock test_ai_sprint09 test_sprint10 -v` para regressão. A suíte não substitui a revisão visual e funcional manual.

## Estrutura
- `main.py`: servidor, autenticação, APIs, migrações e relatórios.
- `database/schema.sql`: esquema SQLite.
- `templates/`, `static/`: interface e responsividade.
- `easystock_ai/`: interpretação e análise somente leitura.
- `docs/API.md`: contrato das APIs e exemplos.
- `docs/VALIDACAO_RC1.md`: roteiro de homologação.
- `test_*.py`: testes automatizados.

## Equipe
Willian Barbosa Vasconcelos — Ciência da Computação, UNINASSAU, turma 8NA — Scrum Master e desenvolvedor.

Repositório: https://github.com/Willvsc/EasyStock
