"""
Inicialização automática do ambiente da aplicação.

Responsável por:
- executar as migrations do Alembic;
- preparar os dados do ambiente demo.

O schema do banco continua sendo controlado exclusivamente pelo Alembic.
"""

from pathlib import Path
from functools import lru_cache

from alembic import command
from alembic.config import Config

from config import (
    APP_ENV,
    INITIAL_ADMIN_NAME,
    INITIAL_ADMIN_PASSWORD,
    INITIAL_ADMIN_USERNAME,
)
from database.connection import SessionLocal
from services.auth_service import (
    DadosUsuarioInvalidosError,
    UsuarioJaExisteError,
    provisionar_admin_inicial,
)


def executar_migrations() -> None:
    """Executa todas as migrations pendentes do banco."""

    raiz_projeto = Path(__file__).resolve().parent.parent
    alembic_ini = raiz_projeto / "alembic.ini"

    config = Config(str(alembic_ini))

    command.upgrade(config, "head")


def provisionar_admin_inicialmente() -> None:
    """Cria o primeiro admin de produção usando secrets externos."""

    valores = (
        INITIAL_ADMIN_USERNAME,
        INITIAL_ADMIN_PASSWORD,
        INITIAL_ADMIN_NAME,
    )

    if not any(valores):
        return

    if not all(valores):
        raise ValueError(
            "Configure INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_PASSWORD e "
            "INITIAL_ADMIN_NAME juntos."
        )

    db = SessionLocal()

    try:
        provisionar_admin_inicial(
            db,
            username=INITIAL_ADMIN_USERNAME,
            senha=INITIAL_ADMIN_PASSWORD,
            nome_completo=INITIAL_ADMIN_NAME,
        )
    except UsuarioJaExisteError:
        pass
    except DadosUsuarioInvalidosError as erro:
        raise ValueError(
            f"Dados do administrador inicial inválidos: {erro}"
        ) from erro
    finally:
        db.close()


@lru_cache(maxsize=1)
def inicializar_aplicacao() -> None:
    """
    Prepara o banco antes da aplicação ser utilizada.

    A inicialização é executada uma única vez por processo. O Streamlit
    reexecuta o script a cada interação, mas não é necessário verificar as
    migrations e os dados demo em todas essas reexecuções.

    Em ambiente demo:
        - executa as migrations;
        - cria os dados fictícios necessários.

    Em outros ambientes:
        - executa somente as migrations.
    """

    executar_migrations()

    if APP_ENV == "production":
        provisionar_admin_inicialmente()

    if APP_ENV == "demo":
        from seed_demo import criar_dados_demo

        criar_dados_demo()