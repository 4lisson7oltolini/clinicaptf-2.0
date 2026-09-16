"""
Fixtures compartilhadas dos testes.

Cada teste utiliza um banco SQLite em memória,
isolado das demais execuções.
"""

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from services.paciente_service import criar_paciente
from services.profissional_service import criar_profissional

import models.paciente  # noqa: F401
import models.profissional  # noqa: F401
import models.consulta  # noqa: F401
import models.usuario  # noqa: F401


@pytest.fixture()
def db_session():
    """
    Cria um banco SQLite em memória para cada teste.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def paciente_e_profissional(db_session):
    """
    Cria um paciente e um profissional para testes
    que precisam trabalhar com consultas.
    """

    paciente = criar_paciente(
        db_session,
        nome="João da Silva",
        cpf="52998224725",
        telefone="47999999999",
        cep="88000000",
    )

    profissional = criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    return paciente, profissional