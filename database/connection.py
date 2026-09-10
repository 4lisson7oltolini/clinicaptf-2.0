"""
Camada de conexão com o banco de dados.

Usa SQLAlchemy para abstrair SQLite (dev) e PostgreSQL (produção)
com o mesmo código.

A criação e alteração das tabelas é responsabilidade do Alembic.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL


connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)


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