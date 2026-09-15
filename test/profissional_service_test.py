import pytest
from services.profissional_service import (
    criar_profissional,
    listar_profissionais,
    buscar_profissional_por_id,
    remover_profissional,
    ProfissionalJaExisteError,
    DadosProfissionalInvalidosError,
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


def test_criar_profissional_com_nome_completo(db_session):
    profissional = criar_profissional(
        db_session,
        nome="João da Silva",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-11111",
    )

    assert profissional.nome == "João da Silva"


def test_criar_profissional_com_doutora(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dra. Maria",
        especialidade="Fisioterapia Esportiva",
        registro_profissional="CREFITO-22222",
    )

    assert profissional.nome == "Dra. Maria"


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
            nome="Dr. Carlos",
            especialidade="Fisioterapia",
            registro_profissional="CREFITO-12345",
        )


def test_rejeita_nome_profissional_invalido(db_session):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="123456",
            especialidade="Fisioterapia",
            registro_profissional="CREFITO-12345",
        )


def test_rejeita_nome_profissional_vazio(db_session):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="",
            especialidade="Fisioterapia",
            registro_profissional="CREFITO-12345",
        )


def test_rejeita_especialidade_vazia(db_session):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="Dr. João",
            especialidade="",
            registro_profissional="CREFITO-12345",
        )


def test_rejeita_especialidade_muito_curta(db_session):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="Dr. João",
            especialidade="AB",
            registro_profissional="CREFITO-12345",
        )


def test_rejeita_registro_profissional_vazio(db_session):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="Dr. João",
            especialidade="Fisioterapia",
            registro_profissional="",
        )


def test_rejeita_registro_profissional_muito_curto(db_session):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="Dr. João",
            especialidade="Fisioterapia",
            registro_profissional="AB",
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
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-22222",
    )

    criar_profissional(
        db_session,
        nome="Dra. Ana",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-33333",
    )

    profissionais = listar_profissionais(db_session)

    nomes = [
        profissional.nome
        for profissional in profissionais
    ]

    assert nomes == sorted(nomes)


def test_lista_profissionais_com_filtro_por_nome(db_session):
    criar_profissional(
        db_session,
        nome="Dr. Carlos",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-11111",
    )

    criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-22222",
    )

    profissionais = listar_profissionais(
        db_session,
        termo_busca="Carlos",
    )

    assert len(profissionais) == 1
    assert profissionais[0].nome == "Dr. Carlos"


def test_busca_profissional_por_id(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-12345",
    )

    encontrado = buscar_profissional_por_id(
        db_session,
        profissional.id,
    )

    assert encontrado is not None
    assert encontrado.id == profissional.id
    assert encontrado.nome == "Dr. João"


def test_busca_profissional_inexistente(db_session):
    profissional = buscar_profissional_por_id(
        db_session,
        999999,
    )

    assert profissional is None


def test_remove_profissional_com_sucesso(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-12345",
    )

    resultado = remover_profissional(
        db_session,
        profissional.id,
    )

    assert resultado is True

    encontrado = buscar_profissional_por_id(
        db_session,
        profissional.id,
    )

    assert encontrado is None


def test_remover_profissional_inexistente(db_session):
    resultado = remover_profissional(
        db_session,
        999999,
    )

    assert resultado is False