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

from config import APP_ENV


def executar_migrations() -> None:
    """Executa todas as migrations pendentes do banco."""

    raiz_projeto = Path(__file__).resolve().parent.parent
    alembic_ini = raiz_projeto / "alembic.ini"

    config = Config(str(alembic_ini))

    command.upgrade(config, "head")


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

    if APP_ENV == "demo":
        from seed_demo import criar_dados_demo

        criar_dados_demo()