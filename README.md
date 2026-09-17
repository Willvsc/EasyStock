# 📦 EasyStock

Sistema web de gerenciamento de estoque desenvolvido com Python, Flask e SQLite.

O EasyStock permite o gerenciamento de produtos, categorias, movimentações de estoque e usuários, contando com autenticação e controle de acesso por perfil.

## 🚀 Funcionalidades

- Login e logout de usuários
- Autenticação com sessão
- Senhas armazenadas com hash
- Controle de acesso por perfil
- Perfis Administrador e Funcionário
- Cadastro e listagem de usuários
- Cadastro de produtos
- Consulta de produtos
- Edição de produtos
- Exclusão de produtos
- Controle de entrada e saída de estoque
- Histórico de movimentações
- Gerenciamento de categorias
- Dashboard com informações do estoque
- Persistência de dados com SQLite

## 🛠️ Tecnologias utilizadas

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Werkzeug

## 📁 Estrutura do projeto

```text
sistema-estoque/
│
├── database/
│   └── schema.sql
│
├── static/
│   ├── app.js
│   └── style.css
│
├── templates/
│   ├── index.html
│   └── login.html
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 💻 Executando o projeto localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/Willvsc/EasyStock.git
```

Entre na pasta:

```bash
cd EasyStock
```

### 2. Criar o ambiente virtual

No Windows:

```powershell
python -m venv venv
```

### 3. Ativar o ambiente virtual

No PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```powershell
pip install -r requirements.txt
```

### 5. Executar o sistema

```powershell
python main.py
```

Na primeira execução, o EasyStock cria automaticamente o banco de dados SQLite, as tabelas necessárias, os perfis padrão, as categorias padrão e o usuário Administrador inicial.

### 6. Acessar no navegador

Abra:

```text
http://127.0.0.1:5000
```

## 🔐 Acesso inicial

Na primeira execução, utilize:

```text
E-mail: admin@easystock.com
Senha: Admin123
```

O Administrador possui acesso ao gerenciamento de usuários e às funcionalidades de estoque.

O perfil Funcionário possui acesso às operações de estoque, sem acesso ao gerenciamento de usuários.

> As credenciais acima são destinadas ao ambiente local de desenvolvimento.

## 🗄️ Banco de dados

O projeto utiliza SQLite.

O arquivo local:

```text
estoque.db
```

não é versionado no GitHub.

Ao iniciar o sistema pela primeira vez, o banco é criado automaticamente pelo EasyStock.

O projeto também possui o modelo SQL em:

```text
database/schema.sql
```

## 👥 Perfis de acesso

### Administrador

Possui acesso às funcionalidades de estoque e ao gerenciamento de usuários.

### Funcionário

Possui acesso às operações de estoque, mas não possui permissão para acessar o gerenciamento de usuários.

## 📌 Projeto acadêmico

Projeto desenvolvido para fins acadêmicos como sistema de gerenciamento de estoque.