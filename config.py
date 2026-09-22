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


def _config_value(name: str) -> str:
    """Lê configuração do ambiente ou dos secrets do Streamlit Cloud."""

    value = os.getenv(name, "").strip()

    if value:
        return value

    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


# ============================================================
# Ambiente da aplicação
# ============================================================

APP_ENV = (_config_value("APP_ENV") or "development").lower()

DATABASE_URL = _config_value("DATABASE_URL")

if APP_ENV == "demo":
    DATABASE_URL = _config_value("DEMO_DATABASE_URL") or (
        "sqlite:///./clinicptf_demo.db"
    )
elif not DATABASE_URL and APP_ENV in {"development", "testing"}:
    DATABASE_URL = "sqlite:///./clinicaptf.db"


# ============================================================
# Chave secreta
# ============================================================

SECRET_KEY = _config_value("SECRET_KEY")

DATABASE_SSLMODE = _config_value("DATABASE_SSLMODE")

INITIAL_ADMIN_USERNAME = _config_value("INITIAL_ADMIN_USERNAME")
INITIAL_ADMIN_PASSWORD = _config_value("INITIAL_ADMIN_PASSWORD")
INITIAL_ADMIN_NAME = _config_value("INITIAL_ADMIN_NAME")

INSECURE_SECRET_KEYS = {
    "change-me-in-your-local-env",
    "defina-uma-chave-segura-fora-do-repositorio",
    "dev-secret-change-me",
}


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
        if APP_ENV == "production":
            raise ValueError(
                "DATABASE_URL não foi definida para produção."
            )

        raise ValueError(
            "DATABASE_URL não foi definida."
        )

    if APP_ENV not in {"development", "testing", "demo", "production"}:
        raise ValueError(
            "APP_ENV inválido. "
            "Use: development, testing, demo ou production."
        )

    if APP_ENV == "production":
        if not DATABASE_URL.startswith(("postgresql://", "postgresql+")):
            raise ValueError(
                "DATABASE_URL de produção deve utilizar PostgreSQL."
            )

        if not SECRET_KEY:
            raise ValueError(
                "SECRET_KEY não foi definida. "
                "Defina uma SECRET_KEY segura no ambiente de produção."
            )

        if (
            len(SECRET_KEY) < 32
            or SECRET_KEY.lower() in INSECURE_SECRET_KEYS
        ):
            raise ValueError(
                "A SECRET_KEY de produção deve ser forte, exclusiva e ter "
                "pelo menos 32 caracteres."
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
