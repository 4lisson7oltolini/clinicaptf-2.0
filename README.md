# Clínica PTF 2.0

Sistema de gerenciamento para clínicas desenvolvido com **Python + Streamlit**, criado como uma evolução arquitetural do projeto Clínica PTF 1.0.

A versão 2.0 foi reconstruída com foco em organização de código, segurança, testes automatizados, persistência de dados, migrações de banco de dados e preparação para deploy.

> **Status:** Em desenvolvimento

---

## Sobre o projeto

O **ClinicPTF 2.0** é um sistema de gerenciamento de clínica desenvolvido como projeto de estudo e portfólio, com foco em práticas utilizadas no desenvolvimento de aplicações reais.

O sistema permite gerenciar:

* Pacientes
* Profissionais
* Consultas
* Usuários
* Dashboard

A principal evolução em relação à primeira versão está na arquitetura.

Em vez de concentrar interface, regras de negócio e acesso ao banco no mesmo código, o projeto foi dividido em camadas independentes:

```text
Interface
    ↓
Pages / Components
    ↓
Services
    ↓
Models
    ↓
Database
    ↓
SQLite / PostgreSQL
```

Essa estrutura facilita manutenção, testes e futuras evoluções do sistema.

---

# Screenshots

### login
![Tela de login da Clínica PTF 2.0](Screenshot/printinicio-1.png)
### Inicio
![Tela de Inicio da Clínica PTF 2.0](Screenshot/printclinica-1.png)
### Pacientes
![Tela de Pacientes da Clínica PTF 2.0](Screenshot/printpacientes-1.png)
### Profissionais
![Tela de Profissionais da Clínica PTF 2.0](Screenshot/printprofissionais-1.png)
### Agenda
![Tela de Agenda da Clínica PTF 2.0](Screenshot/printagenda-1.png)


# Funcionalidades

### Pacientes

* Cadastro de pacientes
* Listagem
* Pesquisa
* Remoção
* Validação de CPF
* Validação de CEP
* Controle de CPF duplicado

### Profissionais

* Cadastro de profissionais
* Listagem
* Especialidade
* Registro profissional
* Controle de registro duplicado

O projeto foi desenvolvido com uma arquitetura em camadas, buscando aplicar boas práticas de desenvolvimento de software e conceitos estudados durante a formação em Desenvolvimento de Sistemas.

Entre os principais recursos estão:

* Autenticação de usuários
* Senhas armazenadas com hash
* Cadastro e gerenciamento de pacientes
* Cadastro e gerenciamento de profissionais
* Gerenciamento de consultas
* Agenda
* Persistência de dados
* Validação de informações
* Migrações de banco de dados
* Testes automatizados
* Ambiente de demonstração
* Integração contínua
* Preparação para deploy
* Suporte a SQLite e PostgreSQL
* Containerização com Docker

---

## Tecnologias utilizadas

### Backend

* Python
* SQLAlchemy
* Alembic
* Pydantic
* Passlib
* bcrypt

### Interface

* Streamlit

### Banco de dados

* SQLite
* PostgreSQL

### Testes

* Pytest
* Pytest-Cov
* Faker

### DevOps

* Git
* GitHub
* GitHub Actions
* Docker

---

## Arquitetura

O projeto utiliza uma arquitetura organizada em camadas para separar responsabilidades.

```text
Interface
   |
   v
Pages / Components
   |
   v
Services
   |
   v
Models
   |
   v
Database
```

---

## Banco de dados

A Clínica PTF 2.0 utiliza **SQLAlchemy** como camada de acesso ao banco de dados.

O controle da estrutura do banco é realizado pelo **Alembic**.

Isso permite versionar alterações no banco de dados e reproduzir a estrutura da aplicação em diferentes ambientes.

### Executar migrations

```bash
alembic upgrade head
```

### Verificar a versão atual

```bash
alembic current
```

### Verificar se existem alterações pendentes

```bash
alembic check
```

O schema do banco é controlado exclusivamente pelas migrations do Alembic.

---

## Inicialização automática

A aplicação possui um mecanismo de inicialização em:

```text
database/initialization.py
```

Durante a inicialização, o sistema:

1. Carrega as configurações do ambiente.
2. Executa as migrations pendentes.
3. Prepara o banco de dados.
4. Caso esteja no ambiente de demonstração, cria os dados fictícios necessários.

Isso permite que o ambiente seja preparado automaticamente antes da utilização da aplicação.

---

## Ambiente de demonstração

O projeto possui um ambiente específico para demonstração.

Para executar:

### Windows PowerShell

```powershell
$env:APP_ENV="demo"
python -m streamlit run app.py
```

O ambiente demo utiliza um banco SQLite separado:

```text
clinicptf_demo.db
```

Os dados utilizados são fictícios e servem exclusivamente para demonstração e testes.

### Credenciais de demonstração

```text
Usuário: demo
Senha: demo1234
```

O ambiente de demonstração cria automaticamente:

* Usuário demo
* Pacientes fictícios
* Profissionais fictícios

---

## Configuração local

Clone o projeto:

```bash
git clone https://github.com/4lisson7oltolini/clinicptf-2.0.git
```

Entre no diretório:

```bash
cd clinicptf-2.0
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Para instalar também as dependências de desenvolvimento:

```bash
python -m pip install -r requirements-dev.txt
```

---

## Variáveis de ambiente

Crie um arquivo:

```text
.env
```

Baseado no:

```text
.env.example
```

Exemplo:

```env
DATABASE_URL=sqlite:///./clinicptf.db

DEMO_DATABASE_URL=sqlite:///./clinicptf_demo.db

APP_ENV=development

SECRET_KEY=change-me-in-your-local-env
```

O arquivo `.env` não deve ser versionado no Git.

---

## Executando a aplicação

Depois de instalar as dependências:

```bash
python -m streamlit run app.py
```

A aplicação será iniciada localmente pelo Streamlit.

---

## Testes

O projeto utiliza **Pytest** para testes automatizados.

Execute todos os testes:

```bash
python -m pytest
```

Para executar com cobertura:

```bash
python -m pytest --cov=.
```

Os testes abrangem principalmente:

* Autenticação
* Usuários
* Pacientes
* Profissionais
* Consultas
* Validações
* Regras dos services

---

## Integração contínua

O projeto possui um workflow do **GitHub Actions**:

```text
.github/workflows/test.yml
```

A cada push e pull request configurado, o workflow:

1. Configura o ambiente Python.
2. Instala as dependências de desenvolvimento.
3. Executa os testes automatizados.
4. Informa se a alteração passou ou falhou.

O objetivo é evitar que alterações com testes quebrados sejam integradas ao projeto sem serem identificadas.

---

## Dependências

As dependências foram separadas em dois arquivos.

### requirements.txt

Contém somente as dependências necessárias para executar a aplicação:

```text
Streamlit
SQLAlchemy
PostgreSQL
Pydantic
python-dotenv
Passlib
bcrypt
Alembic
```

### requirements-dev.txt

Contém as dependências utilizadas durante o desenvolvimento e testes:

```text
pytest
pytest-cov
faker
```

Essa separação facilita a preparação do projeto para ambientes de produção.

---

## Docker

O projeto possui um `Dockerfile` para facilitar a criação de um ambiente isolado.

Para criar a imagem:

```bash
docker build -t clinicaptf .
```

Para executar:

```bash
docker run -p 8501:8501 clinicaptf
```

A aplicação poderá ser acessada pela porta:

```text
8501
```

Para ambientes de produção, recomenda-se utilizar PostgreSQL em vez de SQLite.

---

## PostgreSQL

O sistema foi preparado para trabalhar com PostgreSQL através do SQLAlchemy.

Exemplo de configuração:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/clinicaptf
```

A aplicação identifica o banco através da variável `DATABASE_URL`.

A conexão com SQLite continua disponível para desenvolvimento local e demonstrações.

---

## Segurança

A Clínica PTF 2.0 foi estruturada considerando algumas práticas básicas de segurança.

Entre elas:

* Senhas não são armazenadas em texto puro.
* Senhas são protegidas utilizando hash.
* Informações sensíveis são carregadas através de variáveis de ambiente.
* Arquivos `.env` não são versionados.
* Bancos locais são ignorados pelo Git.
* A aplicação possui controle de sessão.
* O ambiente de produção exige uma `SECRET_KEY` configurada.
* O ambiente demo utiliza dados fictícios.

As credenciais apresentadas neste README são exclusivamente para o ambiente de demonstração.

---

## Desenvolvimento

O desenvolvimento do projeto segue uma organização baseada em branches.

Exemplo:

```text
main
│
└── feature/foundation
```

As alterações são desenvolvidas em branches específicas antes de serem integradas à branch principal.

Exemplo:

```bash
git checkout -b feature/nova-funcionalidade
```

Depois das alterações:

```bash
git add .
git commit -m "feat: add new functionality"
git push origin feature/nova-funcionalidade
```

---

## Roadmap

### Fundação

* [x] Estrutura inicial do projeto
* [x] Arquitetura em camadas
* [x] Configuração por variáveis de ambiente
* [x] SQLAlchemy
* [x] Alembic
* [x] Migrations
* [x] Autenticação
* [x] Hash de senhas
* [x] Testes automatizados
* [x] GitHub Actions
* [x] Ambiente demo
* [x] Dados fictícios
* [x] Configuração do Streamlit
* [x] Docker

### Próximas etapas

* [ ] Melhorar dashboard
* [ ] Melhorar agenda
* [ ] Controle de permissões por usuário
* [ ] Relatórios
* [ ] Exportação de dados
* [ ] Melhorias na experiência do usuário
* [ ] PostgreSQL em ambiente hospedado
* [ ] Deploy público
* [ ] Monitoramento
* [ ] Documentação da API, caso seja adicionada

---

## Objetivo do projeto

A Clínica PTF 2.0 também funciona como projeto de portfólio para demonstrar conhecimentos em:

* Python
* Desenvolvimento web
* Banco de dados
* SQLAlchemy
* Arquitetura de software
* Testes automatizados
* Git e GitHub
* CI/CD
* Docker
* Variáveis de ambiente
* Migrações de banco de dados
* Desenvolvimento de aplicações com Streamlit

O projeto busca demonstrar não apenas a criação de uma interface, mas também a construção de uma aplicação organizada, testável e preparada para evolução.

---

## Aviso

Este projeto possui finalidade educacional e de portfólio.

Os dados utilizados no ambiente de demonstração são fictícios.

A aplicação não deve ser utilizada em produção para armazenamento de informações reais de pacientes sem a implementação de controles adicionais de segurança, privacidade, auditoria, backup e conformidade com a legislação aplicável.

---

## Autor

**Alisson Voltolini**

Estudante de Desenvolvimento de Sistemas e desenvolvedor em formação, com foco em desenvolvimento web, Python, Java, JavaScript, bancos de dados e construção de aplicações para portfólio profissional.

---

## Licença

Este projeto está em desenvolvimento para fins educacionais e de portfólio.
