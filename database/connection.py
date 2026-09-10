"""
Camada de conexão com o banco de dados.
Usa SQLAlchemy para abstrair SQLite (dev) e PostgreSQL (produção) com o mesmo código.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Gera uma sessão de banco e garante o fechamento (usar com 'with' ou try/finally)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria todas as tabelas registradas em Base (chamar uma vez na inicialização)."""
    import models.paciente  # noqa: F401  (garante que o model seja registrado antes do create_all)
    import models.profissional  # noqa: F401
    import models.consulta  # noqa: F401
    import models.usuario  # noqa: F401
    Base.metadata.create_all(bind=engine)