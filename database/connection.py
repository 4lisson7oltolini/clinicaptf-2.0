"""
Camada de conexão com o banco de dados.

Usa SQLAlchemy para abstrair SQLite (dev) e PostgreSQL (produção)
com o mesmo código.

A criação e alteração das tabelas é responsabilidade do Alembic.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base

from config import APP_ENV, DATABASE_SSLMODE, DATABASE_URL


database_url = make_url(DATABASE_URL)

if database_url.get_backend_name() == "sqlite":
    connect_args = {"check_same_thread": False}
elif (
    APP_ENV == "production"
    and database_url.get_backend_name() == "postgresql"
    and "sslmode" not in database_url.query
):
    connect_args = {"sslmode": DATABASE_SSLMODE or "require"}
else:
    connect_args = {}


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    """
    Gera uma sessão de banco de dados e garante seu fechamento.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
