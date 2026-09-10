"""
Fixture compartilhada: cria um banco SQLite em memória do zero para cada teste,
para não depender de Postgres nem sujar dados entre execuções.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
import models.paciente  # noqa: F401
import models.profissional  # noqa: F401
import models.consulta  # noqa: F401
import models.usuario  # noqa: F401


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()