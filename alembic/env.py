from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from config import DATABASE_URL
from database.connection import Base

# Importa os modelos para que o SQLAlchemy registre
# todas as tabelas no Base.metadata.
from models.paciente import Paciente
from models.profissional import Profissional
from models.consulta import Consulta
from models.usuario import Usuario


config = context.config

# Configuração de logging do Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Metadata utilizada pelo Alembic para detectar alterações
# nos modelos.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Executa migrations no modo offline.

    Nesse modo o Alembic gera os comandos SQL sem
    precisar abrir uma conexão com o banco.
    """

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Executa migrations conectando diretamente ao banco.
    """

    configuration = config.get_section(config.config_ini_section)

    configuration["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()