# 🩺 ClinicPTF 2.0

Sistema de gerenciamento para clínicas desenvolvido em **Python + Streamlit**, criado como uma evolução arquitetural da primeira versão do ClinicPTF.

A versão 2.0 foi desenvolvida com foco em **organização de código, separação de responsabilidades, persistência de dados, autenticação, validação, testes automatizados e possibilidade de execução com SQLite ou PostgreSQL**.

---

## 📌 Sobre o projeto

O **ClinicPTF 2.0** é um sistema de gerenciamento de clínica que permite controlar informações de:

* 👤 Pacientes
* 🩺 Profissionais
* 📅 Consultas
* 🔐 Usuários e autenticação
* 📊 Dashboard da clínica

O projeto foi estruturado seguindo uma arquitetura em camadas, evitando concentrar toda a lógica dentro das páginas do Streamlit.

A aplicação utiliza:

* **Streamlit** para interface
* **SQLAlchemy** para comunicação com o banco
* **SQLite** para desenvolvimento local
* **PostgreSQL** como opção para produção
* **Passlib + bcrypt** para armazenamento seguro de senhas
* **Pydantic** e validações próprias para validação de dados
* **Pytest** para testes automatizados
* **Docker** para facilitar a execução em diferentes máquinas

---

# 🏗️ Arquitetura do projeto

A estrutura atual do projeto é:

```text
clinicaptf-2.0/
│
├── components/
│   ├── __init__.py
│   └── paciente_form.py
│
├── database/
│   ├── __init__.py
│   └── connection.py
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
│   ├── conftest.py
│   ├── consulta_service_test.py
│   ├── paciente_service_test.py
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
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

A estrutura está dividida principalmente em seis responsabilidades:

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

Essa separação permite alterar uma camada sem precisar modificar todo o sistema.

---

# 🔄 Como o sistema funciona

O fluxo principal da aplicação é:

```text
Usuário
   │
   ▼
Streamlit
   │
   ▼
Login
   │
   ▼
Auth Service
   │
   ▼
Banco de Dados
   │
   ▼
Usuário autenticado
   │
   ▼
Dashboard
   │
   ├── Pacientes
   ├── Profissionais
   └── Agenda
```

---

# 1. Inicialização da aplicação

O arquivo responsável por iniciar o sistema é:

```text
app.py
```

Ele funciona como o ponto de entrada do Streamlit.

Primeiramente, a aplicação configura a página:

```python
st.set_page_config(
    page_title="ClinicaPTF 2.0",
    page_icon="🩺",
    layout="wide"
)
```

Depois inicializa o banco:

```python
init_db()
```

O `init_db()` cria as tabelas registradas nos modelos caso elas ainda não existam.

O sistema então verifica se existe um usuário autenticado através do:

```python
st.session_state
```

Caso não exista, o usuário é enviado para a tela de login.

Depois da autenticação, o sistema disponibiliza a navegação:

```text
🏠 Início
👤 Pacientes
🩺 Profissionais
📅 Agenda
```

O `app.py` utiliza `st.Page` e `st.navigation` para controlar explicitamente as páginas da aplicação.

---

# 2. Sistema de login

O login é controlado pelo:

```text
services/auth_service.py
```

O sistema **não armazena a senha em texto puro**.

Ao criar um usuário, a senha passa pelo bcrypt:

```python
pwd_context.hash(senha)
```

O banco armazena somente o resultado do hash.

Durante o login, o sistema utiliza:

```python
pwd_context.verify(senha, usuario.senha_hash)
```

Assim, a senha digitada é comparada com o hash armazenado sem precisar guardar a senha original.

---

# 3. Criação do primeiro usuário

O arquivo:

```text
create_admin.py
```

foi criado para facilitar a configuração inicial do sistema.

Execute:

```bash
python create_admin.py
```

O programa solicitará:

```text
Usuário:
Senha:
Nome completo:
```

Depois disso, o usuário será criado no banco.

O script também inicializa o banco antes da criação do usuário.

### Exemplo

```text
Usuário: admin
Senha: ********
Nome completo: Administrador
```

Resultado:

```text
Usuário 'admin' criado com sucesso.
```

---

# 4. Banco de dados

A camada de banco está localizada em:

```text
database/
└── connection.py
```

O projeto utiliza **SQLAlchemy** como ORM.

Isso significa que o código trabalha principalmente com objetos Python em vez de escrever SQL manualmente.

A conexão é criada utilizando:

```python
create_engine(DATABASE_URL)
```

O projeto pode utilizar:

```text
SQLite
```

ou:

```text
PostgreSQL
```

sem precisar modificar a estrutura dos modelos.

A configuração padrão é:

```text
sqlite:///./clinicaptf.db
```

Portanto, se nenhuma variável de ambiente for configurada, o sistema cria um banco SQLite local chamado:

```text
clinicaptf.db
```

A camada `database.connection` também possui `SessionLocal`, `Base`, `get_db()` e `init_db()`.

---

# 5. Configuração do ambiente

As configurações ficam no:

```text
config.py
```

O sistema utiliza `python-dotenv` para carregar variáveis de um arquivo `.env`.

As principais configurações são:

```text
DATABASE_URL
APP_ENV
SECRET_KEY
```

Por padrão:

```text
DATABASE_URL=sqlite:///./clinicaptf.db
APP_ENV=development
SECRET_KEY=dev-secret-change-me
```

Para ambientes reais, recomenda-se alterar principalmente a `SECRET_KEY`.

---

# 6. Modelo de Paciente

O arquivo:

```text
models/paciente.py
```

representa os pacientes do sistema.

A tabela utilizada é:

```text
pacientes
```

Ela possui informações como:

```text
id
nome
cpf
cep
telefone
criado_em
```

O CPF é único no banco.

Além disso, o modelo utiliza validações para CPF e CEP.

---

# 7. Validação de CPF

As validações ficam em:

```text
utils/validators.py
```

O sistema possui uma implementação própria para verificar os dígitos verificadores do CPF.

Exemplo:

```python
validar_cpf("12345678909")
```

O sistema:

1. Remove caracteres não numéricos.
2. Verifica se existem 11 dígitos.
3. Impede sequências como `11111111111`.
4. Calcula os dígitos verificadores.
5. Compara os resultados.

Também existe validação de CEP.

O CEP precisa possuir 8 dígitos numéricos.

---

# 8. Cadastro de pacientes

A interface de cadastro está em:

```text
components/paciente_form.py
```

Esse componente cria o formulário:

```text
Nome
CPF
CEP
Telefone
```

Quando o usuário clica em:

```text
Cadastrar
```

o componente chama:

```python
criar_paciente(...)
```

do:

```text
services/paciente_service.py
```

A página não acessa diretamente o banco para implementar a regra de negócio.

O fluxo é:

```text
Formulário
   ↓
paciente_form.py
   ↓
paciente_service.py
   ↓
Paciente
   ↓
SQLAlchemy
   ↓
Banco
```

---

# 9. Serviço de pacientes

O arquivo:

```text
services/paciente_service.py
```

é responsável pelas regras de negócio dos pacientes.

Ele possui funções para:

* Criar paciente
* Listar pacientes
* Buscar paciente por ID
* Remover paciente
* Pesquisar pacientes pelo nome

Por exemplo:

```python
listar_pacientes(db)
```

retorna os pacientes ordenados pelo nome.

Também existe tratamento para CPF duplicado através de:

```python
PacienteJaExisteError
```

---

# 10. Modelo de profissional

O arquivo:

```text
models/profissional.py
```

representa os profissionais da clínica.

A tabela é:

```text
profissionais
```

Possui:

```text
id
nome
especialidade
registro_profissional
```

O registro profissional é único.

O projeto utiliza como exemplo registros como:

```text
CREFITO-12345
```

O profissional também possui relacionamento com consultas.

---

# 11. Cadastro de profissionais

A página:

```text
pages/2_Profissionais.py
```

possui um formulário para cadastrar:

```text
Nome
Especialidade
Registro profissional
```

Após o envio, a página chama:

```python
criar_profissional(...)
```

do:

```text
services/profissional_service.py
```

Isso mantém a regra de negócio fora da interface.

---

# 12. Modelo de consulta

O arquivo:

```text
models/consulta.py
```

representa uma consulta.

Uma consulta relaciona:

```text
Paciente
      +
Profissional
      +
Data/Hora
```

A tabela possui relacionamento com:

```text
pacientes
profissionais
```

Os status permitidos são:

```text
agendada
confirmada
concluida
cancelada
```

---

# 13. Agendamento

A página:

```text
pages/3_Agenda.py
```

permite selecionar:

```text
Paciente
Profissional
Data
Hora
Observações
```

Depois do envio, o sistema chama:

```python
agendar_consulta(...)
```

A consulta é então salva no banco.

---

# 14. Prevenção de conflito de horários

Uma das regras de negócio importantes do projeto está em:

```text
services/consulta_service.py
```

Antes de cadastrar uma consulta, o sistema verifica se o profissional já possui uma consulta próxima daquele horário.

A duração padrão considerada é:

```python
DURACAO_PADRAO_MINUTOS = 50
```

Caso exista conflito, é lançada:

```python
ConflitoDeHorarioError
```

E a interface informa:

```text
Profissional já tem consulta marcada próxima a esse horário.
```

Isso impede que o mesmo profissional seja agendado para consultas incompatíveis no mesmo período.

---

# 15. Dashboard

A página:

```text
pages/0_Inicio.py
```

funciona como o dashboard inicial.

Ela apresenta informações relacionadas ao dia atual e utiliza os serviços de:

```text
profissionais
consultas
```

Entre as informações utilizadas estão:

* Consultas do dia
* Quantidade de consultas ativas
* Profissionais
* Situação atual dos profissionais

---

# 16. Controle de acesso

As páginas utilizam:

```text
utils/auth_guard.py
```

para verificar se existe um usuário autenticado.

As páginas protegidas executam:

```python
exigir_login()
```

Antes de mostrar o conteúdo.

O fluxo é:

```text
Usuário acessa página
        ↓
exigir_login()
        ↓
Usuário autenticado?
      /   \
    NÃO    SIM
    ↓       ↓
 bloqueia   página
```

Isso evita que páginas internas sejam utilizadas sem login.

---

# 17. Organização em camadas

Um dos principais objetivos da versão 2.0 é evitar código misturado.

### Interface

```text
pages/
components/
```

Responsável por:

* Formulários
* Botões
* Tabelas
* Mensagens
* Navegação

### Regras de negócio

```text
services/
```

Responsável por:

* Criar registros
* Buscar registros
* Agendar consultas
* Verificar conflitos
* Autenticar usuários

### Modelos

```text
models/
```

Responsável por representar as entidades do banco.

### Banco

```text
database/
```

Responsável por:

* Engine
* Sessões
* Conexões
* Inicialização das tabelas

### Utilitários

```text
utils/
```

Responsável por:

* Validações
* Controle de autenticação

Essa divisão torna o projeto mais fácil de manter e testar.

---

# 18. Testes automatizados

Os testes estão dentro de:

```text
test/
```

Atualmente existem testes para:

```text
auth_service
consulta_service
paciente_service
validators
```

O projeto utiliza:

```text
pytest
pytest-cov
faker
```

A configuração está no:

```text
pytest.ini
```

Ela define:

```ini
[pytest]
pythonpath = .
testpaths = test
```

Assim, o Pytest sabe onde encontrar os testes e os módulos do projeto.

---

# 19. Banco isolado para testes

Um ponto importante da arquitetura é que os testes não precisam utilizar o banco principal.

O arquivo:

```text
test/conftest.py
```

cria um SQLite em memória:

```text
sqlite:///:memory:
```

Isso significa que:

* Os testes não alteram o banco real.
* Cada execução começa com um banco limpo.
* Os testes podem ser executados sem PostgreSQL.
* Os dados dos testes desaparecem ao final da execução.

---

# 20. Dependências

Todas as dependências ficam no:

```text
requirements.txt
```

Entre elas:

```text
Streamlit
SQLAlchemy
psycopg2
Pydantic
python-dotenv
Passlib
bcrypt
Pytest
pytest-cov
Faker
```

---

# 🚀 Como instalar em outra máquina

## 1. Instalar Python

Recomenda-se utilizar **Python 3.12**, especialmente porque o Dockerfile do projeto utiliza:

```text
python:3.12-slim
```

Depois de instalar o Python, confirme:

```bash
python --version
```

Exemplo:

```text
Python 3.12.x
```

---

# 2. Clonar o projeto

No terminal:

```bash
git clone https://github.com/4lisson7oltolini/clinicaptf-2.0.git
```

Entrar na pasta:

```bash
cd clinicaptf-2.0
```

---

# 3. Criar ambiente virtual

Windows:

```powershell
python -m venv .venv
```

Linux/macOS:

```bash
python3 -m venv .venv
```

---

# 4. Ativar o ambiente virtual

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

Depois de ativado, o terminal deverá mostrar algo semelhante a:

```text
(.venv)
```

---

# 5. Atualizar o pip

```bash
python -m pip install --upgrade pip
```

---

# 6. Instalar as dependências

Execute na raiz do projeto:

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` já contém as dependências necessárias para a aplicação e também para execução dos testes.

---

# 7. Criar o usuário administrador

Depois da instalação:

```bash
python create_admin.py
```

Informe:

```text
Usuário:
Senha:
Nome completo:
```

---

# 8. Executar a aplicação

Na raiz do projeto:

```bash
streamlit run app.py
```

O Streamlit normalmente disponibilizará a aplicação em:

```text
http://localhost:8501
```

Abra esse endereço no navegador.

---

# 🔐 Primeiro acesso

Na tela de login, utilize o usuário criado através do:

```bash
python create_admin.py
```

Exemplo:

```text
Usuário: admin
Senha: sua_senha
```

Depois do login, o sistema apresenta:

```text
🏠 Início
👤 Pacientes
🩺 Profissionais
📅 Agenda
```

---

# 🐳 Executando com Docker

O projeto também possui um:

```text
Dockerfile
```

A imagem utiliza:

```text
python:3.12-slim
```

instala as dependências do `requirements.txt`, copia o projeto e inicia o Streamlit na porta `8501`.

## 1. Criar a imagem

Na raiz do projeto:

```bash
docker build -t clinicaptf-2 .
```

---

## 2. Executar o container

```bash
docker run -p 8501:8501 clinicaptf-2
```

Depois abra:

```text
http://localhost:8501
```

---

# 🐳 Docker com banco persistente

Por padrão, o SQLite dentro de um container pode ser perdido quando o container for removido.

Para manter o banco no computador host, recomenda-se utilizar um volume:

```bash
docker run \
  -p 8501:8501 \
  -v clinicaptf_data:/app \
  clinicaptf-2
```

Para ambientes de produção, recomenda-se utilizar PostgreSQL em vez de depender do SQLite dentro do container.

---

# 🐘 Utilizando PostgreSQL

O projeto foi estruturado para aceitar PostgreSQL através da variável:

```text
DATABASE_URL
```

Exemplo:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/clinicaptf
APP_ENV=production
SECRET_KEY=uma-chave-secreta-forte
```

O código de conexão utiliza a mesma camada SQLAlchemy para SQLite e PostgreSQL.

---

# ⚙️ Arquivo `.env`

Para configurar o ambiente local, crie:

```text
.env
```

Exemplo:

```env
DATABASE_URL=sqlite:///./clinicaptf.db
APP_ENV=development
SECRET_KEY=troque-esta-chave
```

Em produção:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/clinicaptf
APP_ENV=production
SECRET_KEY=chave-secreta-segura
```

### ⚠️ Importante

Nunca publique:

```text
.env
```

no GitHub.

Senhas, chaves secretas e credenciais devem permanecer fora do código-fonte.

---

# 🧪 Executando os testes

Com o ambiente virtual ativado:

```bash
pytest
```

Para obter cobertura:

```bash
pytest --cov
```

Ou:

```bash
pytest --cov=. --cov-report=term-missing
```

Os testes utilizam banco SQLite em memória, portanto não dependem do banco de produção.

---

# 🔍 Fluxo completo de uma operação

Por exemplo, quando um paciente é cadastrado:

```text
1. Usuário acessa Pacientes
             ↓
2. Streamlit apresenta formulário
             ↓
3. Usuário informa os dados
             ↓
4. paciente_form.py recebe os dados
             ↓
5. paciente_service.py aplica a regra de negócio
             ↓
6. Paciente recebe os dados
             ↓
7. validators.py valida CPF/CEP
             ↓
8. SQLAlchemy cria o registro
             ↓
9. Banco salva os dados
             ↓
10. Streamlit apresenta mensagem de sucesso
```

Esse fluxo demonstra a principal diferença arquitetural da versão 2.0 em relação a uma aplicação onde interface e banco ficam misturados.

---

# 🧠 Tecnologias utilizadas

| Tecnologia    | Função                       |
| ------------- | ---------------------------- |
| Python        | Linguagem principal          |
| Streamlit     | Interface web                |
| SQLAlchemy    | ORM e acesso ao banco        |
| SQLite        | Banco local/desenvolvimento  |
| PostgreSQL    | Banco para produção          |
| Passlib       | Gerenciamento de hashes      |
| bcrypt        | Hash de senhas               |
| Pydantic      | Validação/modelagem          |
| python-dotenv | Variáveis de ambiente        |
| Pytest        | Testes automatizados         |
| pytest-cov    | Cobertura dos testes         |
| Faker         | Geração de dados para testes |
| Docker        | Containerização              |

---

# 📁 Responsabilidade de cada pasta

## `components/`

Componentes reutilizáveis da interface.

Atualmente possui:

```text
paciente_form.py
```

Responsável pelo formulário de cadastro de pacientes.

---

## `database/`

Camada de acesso ao banco.

Principal arquivo:

```text
connection.py
```

Responsável por:

* Criar engine
* Criar sessões
* Inicializar tabelas
* Gerenciar conexão

---

## `models/`

Modelos ORM:

```text
Paciente
Profissional
Consulta
Usuario
```

Eles representam as entidades persistidas no banco.

---

## `pages/`

Interface da aplicação:

```text
0_Inicio.py
1_Pacientes.py
2_Profissionais.py
3_Agenda.py
```

Cada arquivo representa uma área do sistema.

---

## `services/`

Regras de negócio.

```text
auth_service.py
consulta_service.py
paciente_service.py
profissional_service.py
```

Essa camada é uma das partes mais importantes da arquitetura.

---

## `utils/`

Funções auxiliares.

```text
auth_guard.py
validators.py
```

---

## `test/`

Testes automatizados.

```text
auth_service_test.py
consulta_service_test.py
paciente_service_test.py
test_validators.py
conftest.py
```

---

# 🔒 Segurança

O projeto possui algumas medidas importantes:

### Senhas

As senhas não são armazenadas diretamente.

É utilizado:

```text
bcrypt
```

para gerar hashes.

### Autenticação

As páginas internas utilizam:

```python
exigir_login()
```

para verificar a autenticação.

### Banco

O SQLAlchemy é utilizado como camada ORM.

### Configuração

Credenciais e configurações podem ser fornecidas através de:

```text
.env
```

em vez de ficarem diretamente no código.

---

# ⚠️ Observações importantes

O ClinicPTF 2.0 é um projeto de desenvolvimento e estudo.

Antes de utilizar o sistema em uma clínica real, ainda devem ser avaliados aspectos como:

* LGPD
* Controle de permissões por usuário
* Auditoria
* Backup
* Criptografia
* Gestão de sessões
* Segurança da infraestrutura
* HTTPS
* Política de retenção de dados
* Recuperação de desastres
* Logs
* Controle de acesso granular

Portanto, o projeto **não deve ser considerado automaticamente pronto para produção apenas por possuir autenticação e banco de dados**.

---

# 🚧 Próximos passos sugeridos

Algumas evoluções naturais para o projeto são:

* [ ] Sistema de permissões por função
* [ ] Administrador / profissional
* [ ] Edição de pacientes
* [ ] Exclusão com confirmação
* [ ] Histórico de consultas
* [ ] Prontuário eletrônico
* [ ] Relatórios
* [ ] Exportação para PDF
* [ ] Backup automático
* [ ] PostgreSQL como banco padrão de produção
* [ ] Migrações com Alembic
* [ ] Logs de auditoria
* [ ] CI/CD com GitHub Actions
* [ ] Testes de integração
* [ ] Testes de interface
* [ ] Docker Compose
* [ ] Deploy em servidor
* [ ] HTTPS
* [ ] Controle de permissões
* [ ] Melhorias de UX/UI

---

# 📌 Resumo da arquitetura

O ClinicPTF 2.0 pode ser resumido da seguinte maneira:

```text
                    ┌──────────────────┐
                    │     Usuário      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Streamlit     │
                    │ pages/components │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Services      │
                    │ Regras negócio   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      Models      │
                    │    SQLAlchemy    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Database     │
                    │ SQLite/Postgres  │
                    └──────────────────┘
```

---

# ▶️ Guia rápido

Para quem já possui Python instalado:

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

# 👨‍💻 Autor

**Alisson**

Projeto desenvolvido como evolução do ClinicPTF 1.0, com foco em aprendizado de desenvolvimento de sistemas, arquitetura de software, banco de dados, testes automatizados e boas práticas de programação.

---

# 📜 Status

🟡 **Em desenvolvimento**

O projeto possui uma base funcional e organizada, mas continua em evolução.

A versão 2.0 representa uma reconstrução arquitetural do sistema original, buscando melhorar:

* Organização
* Manutenibilidade
* Testabilidade
* Segurança
* Escalabilidade
* Separação de responsabilidades
* Facilidade de implantação
