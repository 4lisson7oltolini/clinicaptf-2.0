"""
Configurações da aplicação ClinicPTF 2.0.

As configurações são carregadas através de variáveis de ambiente
definidas no arquivo .env.

Nunca coloque senhas, tokens ou chaves reais diretamente neste arquivo.
"""

import os

from dotenv import load_dotenv


# ============================================================
# Carregamento das variáveis de ambiente
# ============================================================

load_dotenv()


# ============================================================
# Ambiente da aplicação
# ============================================================

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if APP_ENV == "demo":
    DATABASE_URL = os.getenv(
        "DEMO_DATABASE_URL",
        "sqlite:///./clinicaptf_demo.db",
    ).strip()
elif not DATABASE_URL:
    DATABASE_URL = "sqlite:///./clinicaptf.db"


# ============================================================
# Chave secreta
# ============================================================

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()


# ============================================================
# Validação das configurações
# ============================================================

def validate_config() -> None:
    """
    Valida as configurações necessárias para executar a aplicação.

    Em desenvolvimento:
        Permite utilizar uma chave padrão para facilitar o desenvolvimento.

    Em produção:
        Exige uma SECRET_KEY definida através do arquivo .env
        ou das variáveis de ambiente do servidor.
    """

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL não foi definida."
        )

    if APP_ENV not in {"development", "testing", "demo", "production"}:
        raise ValueError(
            "APP_ENV inválido. "
            "Use: development, testing, demo ou production."
        )

    if APP_ENV == "production":
        if not SECRET_KEY:
            raise ValueError(
                "SECRET_KEY não foi definida. "
                "Defina uma SECRET_KEY segura no ambiente de produção."
            )

        if SECRET_KEY == "dev-secret-change-me":
            raise ValueError(
                "A SECRET_KEY padrão não pode ser utilizada em produção."
            )


# ============================================================
# Chave padrão apenas para desenvolvimento
# ============================================================

if not SECRET_KEY and APP_ENV == "development":
    SECRET_KEY = "dev-secret-change-me"


# ============================================================
# Executa as validações
# ============================================================

validate_config()
