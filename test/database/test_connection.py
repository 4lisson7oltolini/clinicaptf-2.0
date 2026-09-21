from unittest.mock import Mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database.connection as connection


def test_get_db_fecha_a_sessao_ao_encerrar_o_generator(monkeypatch):
    session = Mock()
    monkeypatch.setattr(connection, "SessionLocal", lambda: session)

    generator = connection.get_db()

    assert next(generator) is session

    generator.close()

    session.close.assert_called_once_with()


def test_base_e_sessionlocal_podem_operar_com_sqlite_isolado():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    testing_session = sessionmaker(bind=engine)
    session = testing_session()

    try:
        assert connection.Base is not None
        assert session.bind is engine
    finally:
        session.close()
        engine.dispose()
