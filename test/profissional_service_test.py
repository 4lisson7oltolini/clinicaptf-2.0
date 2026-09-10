import pytest

from services.profissional_service import (
    criar_profissional,
    listar_profissionais,
    buscar_profissional_por_id,
    ProfissionalJaExisteError,
)


def test_criar_profissional_com_sucesso(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia Ortopédica",
        registro_profissional="CREFITO-12345",
    )

    assert profissional.id is not None
    assert profissional.nome == "Dr. João"
    assert profissional.especialidade == "Fisioterapia Ortopédica"
    assert profissional.registro_profissional == "CREFITO-12345"


def test_nao_permite_registro_profissional_duplicado(db_session):
    criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-12345",
    )

    with pytest.raises(ProfissionalJaExisteError):
        criar_profissional(
            db_session,
            nome="Dra. Maria",
            especialidade="Fisioterapia Neurológica",
            registro_profissional="CREFITO-12345",
        )


def test_lista_profissionais_em_ordem_alfabetica(db_session):
    criar_profissional(
        db_session,
        nome="Dr. Carlos",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-11111",
    )

    criar_profissional(
        db_session,
        nome="Dra. Ana",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-22222",
    )

    profissionais = listar_profissionais(db_session)

    assert len(profissionais) == 2
    assert profissionais[0].nome == "Dr. Carlos"
    assert profissionais[1].nome == "Dra. Ana"


def test_busca_profissional_por_id(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-12345",
    )

    resultado = buscar_profissional_por_id(
        db_session,
        profissional.id,
    )

    assert resultado is not None
    assert resultado.id == profissional.id
    assert resultado.nome == "Dr. João"


def test_busca_profissional_inexistente_retorna_none(db_session):
    resultado = buscar_profissional_por_id(
        db_session,
        profissional_id=9999,
    )

    assert resultado is None