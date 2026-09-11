# ClinicaPTF 2.0

Sistema de gerenciamento para clínicas desenvolvido com **Python + Streamlit**, criado como uma evolução arquitetural do ClinicPTF 1.0.

A versão 2.0 foi reconstruída com foco em:

* Arquitetura em camadas
* Autenticação e hash seguro de senhas
* Persistência com SQLAlchemy
* Migrações com Alembic
* Testes automatizados com Pytest
* Integração contínua com GitHub Actions
* Ambiente de demonstração isolado
* Compatibilidade com PostgreSQL
* Containerização com Docker
* Preparação para deploy

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

### Agenda

* Agendamento de consultas
* Seleção de paciente
* Seleção de profissional
* Data e horário
* Observações
* Status da consulta
* Verificação de conflitos de horário

### Autenticação

* Login de usuários
* Hash de senhas com bcrypt
* Controle de sessão
* Proteção das páginas internas
* Criação inicial de administrador

### Dashboard

* Consultas
* Profissionais
* Informações da agenda
* Indicadores da clínica

---

# Arquitetura

O projeto utiliza uma arquitetura organizada em camadas.

```text
                    ┌───────────────────┐
                    │      Usuário      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     Streamlit     │
                    │ Pages / Components│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     Services      │
                    │ Regras de negócio │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      Models       │
                    │     SQLAlchemy    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      Database     │
                    │ SQLite / Postgres │
                    └───────────────────┘
```

A separação de responsabilidades permite modificar uma camada sem precisar alterar toda a aplicação.

---

# Estrutura do projeto

```text
clinicaptf-2.0/
│
├── .github/
│   └── workflows/
│       └── test.yml
│
├── .streamlit/
│   └── config.toml
│
├── alembic/
│   ├── versions/
│   │   └── 93bf205e4433_create_initial_database_schema.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── components/
│   ├── __init__.py
│   └── paciente_form.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── initialization.py
│
├── models/
│   ├── __init__.py
│   ├── consulta.py
│   ├── paciente.py
│   ├── profissional.py
│   └── usuario.py
│
├── pages/
│   ├── 0_Inicio.py
│   ├── 1_Pacientes.py
│   ├── 2_Profissionais.py
│   └── 3_Agenda.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── consulta_service.py
│   ├── paciente_service.py
│   └── profissional_service.py
│
├── test/
│   ├── __init__.py
│   ├── auth_service_test.py
│   ├── consulta_service_test.py
│   ├── conftest.py
│   ├── paciente_service_test.py
│   ├── profissional_service_test.py
│   └── test_validators.py
│
├── utils/
│   ├── __init__.py
│   ├── auth_guard.py
│   └── validators.py
│
├── app.py
├── config.py
├── create_admin.py
├── seed_demo.py
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── .gitignore
```

---

# Responsabilidade das camadas

## `pages/`

Interface principal da aplicação.

Contém:

```text
0_Inicio.py
1_Pacientes.py
2_Profissionais.py
3_Agenda.py
```

Responsável por:

* Interface
* Formulários
* Tabelas
* Navegação
* Mensagens ao usuário

---

## `components/`

Componentes reutilizáveis da interface.

Exemplo:

```text
paciente_form.py
```

Responsável pelo formulário de cadastro de pacientes.

---

## `services/`

Contém as principais regras de negócio:

```text
auth_service.py
consulta_service.py
paciente_service.py
profissional_service.py
```

Exemplos:

* Criar pacientes
* Criar profissionais
* Autenticar usuários
* Agendar consultas
* Verificar conflitos de horários
* Buscar registros
* Remover registros

As páginas não precisam implementar diretamente essas regras.

---

## `models/`

Contém os modelos ORM do SQLAlchemy:

```text
Paciente
Profissional
Consulta
Usuario
```

Eles representam as entidades persistidas no banco.

---

## `database/`

Responsável pela infraestrutura de banco.

```text
connection.py
initialization.py
```

`connection.py` gerencia:

* Engine
* Sessões
* Conexões
* SQLAlchemy Base

`initialization.py` é responsável pela inicialização automática do ambiente.

---

## `utils/`

Funções auxiliares:

```text
auth_guard.py
validators.py
```

Inclui:

* Validação de CPF
* Validação de CEP
* Controle de autenticação

---

# Banco de dados

O projeto utiliza **SQLAlchemy** como ORM.

Atualmente é possível trabalhar com:

```text
SQLite
PostgreSQL
```

O banco utilizado depende da variável:

```env
DATABASE_URL
```

### Desenvolvimento

Por padrão:

```env
DATABASE_URL=sqlite:///./clinicaptf.db
```

### Produção

Exemplo:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/clinicaptf
```

A aplicação mantém a mesma camada ORM para os dois bancos.

---

# Migrações com Alembic

O schema do banco é controlado pelo **Alembic**.

A migration inicial está localizada em:

```text
alembic/versions/
```

Migration atual:

```text
93bf205e4433_create_initial_database_schema.py
```

Para atualizar o banco:

```bash
alembic upgrade head
```

Para verificar a migration atual:

```bash
alembic current
```

Para verificar se existem alterações de schema não migradas:

```bash
alembic check
```

Essa abordagem mantém o schema do banco versionado e controlado pelo projeto.

---

# Inicialização automática

O arquivo:

```text
database/initialization.py
```

centraliza a preparação do ambiente.

Durante a inicialização:

```text
Aplicação
    ↓
Inicialização
    ↓
Alembic
    ↓
upgrade head
    ↓
Banco atualizado
```

No ambiente `demo`, também são criados automaticamente dados fictícios.

---

# Ambiente Demo

O projeto possui um ambiente específico para demonstração:

```env
APP_ENV=demo
```

Nesse ambiente, a aplicação utiliza:

```text
clinicaptf_demo.db
```

O banco é criado automaticamente e recebe dados fictícios para facilitar a demonstração.

### Dados incluídos

Pacientes de exemplo:

```text
Maria Silva
João Souza
Ana Costa
```

Profissionais de exemplo:

```text
Dra. Ana Oliveira
Dr. Carlos Mendes
```

Também é criado automaticamente o usuário:

```text
Usuário: demo
Senha: demo1234
```

> Os dados acima são exclusivamente fictícios e destinados à demonstração.

---

# Executando localmente

## 1. Clonar o projeto

```bash
git clone https://github.com/4lisson7oltolini/clinicaptf-2.0.git
```

Entrar na pasta:

```bash
cd clinicaptf-2.0
```

---

## 2. Criar ambiente virtual

### Windows

```powershell
python -m venv .venv
```

### Linux/macOS

```bash
python3 -m venv .venv
```

---

## 3. Ativar o ambiente virtual

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

---

## 4. Atualizar o pip

```bash
python -m pip install --upgrade pip
```

---

## 5. Instalar dependências

Para executar a aplicação:

```bash
pip install -r requirements.txt
```

Para desenvolvimento e testes:

```bash
pip install -r requirements-dev.txt
```

O arquivo de desenvolvimento inclui as dependências de runtime e ferramentas como:

```text
pytest
pytest-cov
faker
```

---

# Configuração do ambiente

Crie um arquivo:

```text
.env
```

A partir do exemplo:

```text
.env.example
```

Exemplo:

```env
DATABASE_URL=sqlite:///./clinicaptf.db

DEMO_DATABASE_URL=sqlite:///./clinicaptf_demo.db

APP_ENV=development

SECRET_KEY=troque-esta-chave
```

O arquivo `.env` é ignorado pelo Git e **não deve ser publicado**.

---

# Criando um usuário administrador

Para o ambiente de desenvolvimento:

```bash
python create_admin.py
```

O script solicitará:

```text
Usuário:
Senha:
Nome completo:
```

O usuário será armazenado no banco com a senha protegida por hash.

---

# Executando a aplicação

Na raiz do projeto:

```bash
streamlit run app.py
```

A aplicação estará disponível normalmente em:

```text
http://localhost:8501
```

---

# Executando o Demo localmente

Para iniciar o ambiente de demonstração:

### PowerShell

```powershell
$env:APP_ENV="demo"
python -m streamlit run app.py
```

A aplicação executará automaticamente:

```text
Alembic
   ↓
Banco demo
   ↓
Dados fictícios
   ↓
Usuário demo
   ↓
Aplicação
```

### Login

```text
Usuário: demo
Senha: demo1234
```

---

# Testes automatizados

O projeto utiliza:

* Pytest
* pytest-cov
* Faker

Os testes estão em:

```text
test/
```

Para executar:

```bash
python -m pytest
```

Para cobertura:

```bash
python -m pytest --cov
```

Os testes abrangem principalmente:

```text
Auth Service
Consulta Service
Paciente Service
Profissional Service
Validators
```

---

# Banco isolado para testes

Os testes utilizam um banco SQLite em memória.

Isso permite executar os testes sem alterar o banco utilizado pela aplicação.

```text
Testes
   ↓
SQLite em memória
   ↓
Dados temporários
```

Assim:

* O banco de desenvolvimento não é alterado.
* Os testes começam com um ambiente isolado.
* Não é necessário PostgreSQL para executar a suíte.
* Os dados desaparecem após os testes.

---

# Integração contínua

O projeto utiliza **GitHub Actions** para executar os testes automaticamente.

Workflow:

```text
.github/
└── workflows/
    └── test.yml
```

O pipeline executa:

```text
Git Push / Pull Request
        ↓
Checkout
        ↓
Configuração do Python
        ↓
Instalação das dependências
        ↓
Pytest
        ↓
Resultado
```

As dependências de desenvolvimento são instaladas através de:

```bash
pip install -r requirements-dev.txt
```

Isso mantém as dependências de runtime separadas das ferramentas utilizadas apenas durante desenvolvimento e CI.

---

# Qualidade do código

O projeto utiliza algumas práticas para manter a base organizada:

* Separação de responsabilidades
* Services para regras de negócio
* Models para persistência
* Components reutilizáveis
* Testes automatizados
* Variáveis de ambiente
* Migrações versionadas
* `.gitignore`
* CI com GitHub Actions
* Ambiente demo separado

---

# Autenticação e segurança

As senhas **não são armazenadas em texto puro**.

O sistema utiliza:

```text
Passlib
+
bcrypt
```

Para criação da senha:

```python
pwd_context.hash(senha)
```

Para autenticação:

```python
pwd_context.verify(
    senha,
    usuario.senha_hash
)
```

As páginas protegidas utilizam:

```text
utils/auth_guard.py
```

para verificar se existe uma sessão autenticada.

---

# Modelo de autenticação

O fluxo de login é:

```text
Usuário
   ↓
Tela de Login
   ↓
Auth Service
   ↓
Banco
   ↓
Verificação do hash
   ↓
Session State
   ↓
Dashboard
```

Depois da autenticação, o usuário pode acessar:

```text
Início
Pacientes
Profissionais
Agenda
```

---

# Controle de conflitos de agenda

O serviço de consultas verifica conflitos de horário antes de realizar um novo agendamento.

A duração padrão utilizada é:

```text
50 minutos
```

Quando existe conflito, o serviço gera:

```text
ConflitoDeHorarioError
```

Isso evita que um mesmo profissional seja agendado para consultas incompatíveis no mesmo período.

---

# Docker

O projeto possui um `Dockerfile` para facilitar a execução em ambientes isolados.

Construir a imagem:

```bash
docker build -t clinicaptf-2 .
```

Executar:

```bash
docker run -p 8501:8501 clinicaptf-2
```

A aplicação ficará disponível em:

```text
http://localhost:8501
```

> Para produção, recomenda-se utilizar PostgreSQL em vez de depender de SQLite dentro de um container.

---

# Dependências

## Runtime

O arquivo:

```text
requirements.txt
```

contém as dependências necessárias para executar a aplicação.

Principais tecnologias:

```text
Streamlit
SQLAlchemy
Alembic
psycopg2-binary
Pydantic
python-dotenv
Passlib
bcrypt
```

## Desenvolvimento

O arquivo:

```text
requirements-dev.txt
```

estende as dependências de runtime e adiciona:

```text
pytest
pytest-cov
faker
```

---

# Deploy

O projeto foi preparado para execução como aplicação web através do **Streamlit Community Cloud**.

A configuração visual da aplicação está em:

```text
.streamlit/config.toml
```

O arquivo define:

* Tema
* Cores
* Configurações do servidor
* Aparência da aplicação

O ambiente de demonstração utiliza SQLite e inicialização automática através do Alembic.

> Como o armazenamento local do Streamlit Community Cloud não deve ser tratado como armazenamento persistente, o SQLite é utilizado aqui principalmente para demonstração. Para uma aplicação real, a arquitetura deve utilizar PostgreSQL ou outro banco persistente.

---

# Fluxo de cadastro de paciente

Um exemplo do fluxo arquitetural:

```text
Usuário
   ↓
Página Pacientes
   ↓
paciente_form.py
   ↓
paciente_service.py
   ↓
Validações
   ↓
Modelo Paciente
   ↓
SQLAlchemy
   ↓
Banco de dados
```

A interface não precisa conhecer detalhes da persistência.

Essa separação facilita a realização de testes unitários sobre as regras de negócio.

---

# Tecnologias utilizadas

| Tecnologia         | Utilização                     |
| ------------------ | ------------------------------ |
| **Python**         | Linguagem principal            |
| **Streamlit**      | Interface web                  |
| **SQLAlchemy**     | ORM e persistência             |
| **Alembic**        | Migrações do banco             |
| **SQLite**         | Desenvolvimento e demonstração |
| **PostgreSQL**     | Opção para produção            |
| **Passlib**        | Gerenciamento de hashes        |
| **bcrypt**         | Hash de senhas                 |
| **Pydantic**       | Modelagem/validação            |
| **python-dotenv**  | Variáveis de ambiente          |
| **Pytest**         | Testes automatizados           |
| **pytest-cov**     | Cobertura de testes            |
| **Faker**          | Dados para testes              |
| **Docker**         | Containerização                |
| **GitHub Actions** | Integração contínua            |

---

# Principais diretórios

| Diretório     | Responsabilidade                 |
| ------------- | -------------------------------- |
| `components/` | Componentes reutilizáveis        |
| `database/`   | Conexão e inicialização do banco |
| `models/`     | Modelos SQLAlchemy               |
| `pages/`      | Interface Streamlit              |
| `services/`   | Regras de negócio                |
| `utils/`      | Validações e autenticação        |
| `test/`       | Testes automatizados             |
| `alembic/`    | Migrações do banco               |
| `.github/`    | Workflows do GitHub Actions      |
| `.streamlit/` | Configuração do Streamlit        |

---

# Roadmap

### Arquitetura e infraestrutura

* [x] Separação em camadas
* [x] SQLAlchemy
* [x] SQLite
* [x] Suporte a PostgreSQL
* [x] Alembic
* [x] Variáveis de ambiente
* [x] Ambiente demo
* [x] Docker
* [x] GitHub Actions
* [x] Testes automatizados

### Sistema

* [x] Autenticação
* [x] Pacientes
* [x] Profissionais
* [x] Agenda
* [x] Dashboard
* [x] Validação de CPF
* [x] Validação de CEP
* [x] Controle de conflitos de agenda

### Próximas evoluções

* [ ] Sistema de permissões por função
* [ ] Perfil Administrador / Profissional
* [ ] Edição de pacientes
* [ ] Histórico de consultas
* [ ] Prontuário eletrônico
* [ ] Relatórios
* [ ] Exportação para PDF
* [ ] Logs de auditoria
* [ ] Backup automático
* [ ] Testes de integração
* [ ] Testes de interface
* [ ] Docker Compose
* [ ] PostgreSQL no ambiente de produção
* [ ] HTTPS
* [ ] Melhorias de UX/UI

---

# Sobre produção

O ClinicPTF 2.0 é um projeto de estudo e portfólio.

Apesar de possuir autenticação, persistência, testes e uma arquitetura organizada, **não deve ser considerado automaticamente pronto para utilização em uma clínica real**.

Uma implantação real exigiria, entre outros pontos:

* LGPD
* Controle de acesso granular
* Auditoria
* Backup
* Criptografia
* HTTPS
* Gerenciamento seguro de sessões
* Logs
* Monitoramento
* Política de retenção de dados
* Recuperação de desastres
* Hardening da infraestrutura

---

# Segurança do repositório

Arquivos sensíveis não devem ser versionados.

O projeto ignora:

```text
.env
*.db
*.sqlite
*.sqlite3
__pycache__/
.pytest_cache/
```

As configurações podem ser fornecidas através de variáveis de ambiente.

O arquivo:

```text
.env.example
```

serve apenas como modelo.

---

# Guia rápido

Para executar rapidamente em uma máquina com Python instalado:

```bash
git clone https://github.com/4lisson7oltolini/clinicaptf-2.0.git

cd clinicaptf-2.0

python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Depois:

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt

python create_admin.py

streamlit run app.py
```

Acesse:

```text
http://localhost:8501
```

---

# Guia rápido — Demo

Para executar a versão de demonstração:

```powershell
$env:APP_ENV="demo"
python -m streamlit run app.py
```

Credenciais:

```text
Usuário: demo
Senha: demo1234
```

---

# Autor

**Alisson**

Estudante de Desenvolvimento de Sistemas e desenvolvedor do ClinicPTF 2.0.

O projeto foi desenvolvido como evolução do ClinicPTF 1.0, com foco em:

* Desenvolvimento web
* Python
* Arquitetura de software
* Banco de dados
* Testes automatizados
* Segurança
* Git/GitHub
* CI/CD
* Boas práticas de desenvolvimento

---

# Licença

Projeto desenvolvido para fins educacionais, de estudo e portfólio.

---

## ClinicPTF 2.0

Uma reconstrução arquitetural do ClinicPTF, buscando transformar um projeto inicial em uma aplicação mais organizada, testável e preparada para evolução.

```text
ClinicPTF 1.0
      ↓
Reconstrução arquitetural
      ↓
ClinicPTF 2.0
      ↓
Arquitetura em camadas
      ↓
Testes + CI
      ↓
Demo + Deploy
```
