import pytest

from services.paciente_service import (
    criar_paciente,
    listar_pacientes,
    buscar_por_id,
    remover_paciente,
    PacienteJaExisteError,
)

def test_criar_e_listar_paciente(db_session):
    criar_paciente(db_session, nome="Maria Silva", cpf="111.444.777-35", cep="01311-000")

    pacientes = listar_pacientes(db_session)

    assert len(pacientes) == 1
    assert pacientes[0].nome == "Maria Silva"
    assert pacientes[0].cpf == "11144477735"  # armazenado limpo, sem máscara


def test_nao_permite_cpf_duplicado(db_session):
    criar_paciente(db_session, nome="Maria Silva", cpf="11144477735", cep="01311000")

    with pytest.raises(PacienteJaExisteError):
        criar_paciente(db_session, nome="Outra Pessoa", cpf="11144477735", cep="20000000")


def test_rejeita_cpf_invalido(db_session):
    with pytest.raises(ValueError):
        criar_paciente(db_session, nome="Fulano", cpf="12345678900", cep="01311000")

def test_rejeita_cep_invalido(db_session):
    with pytest.raises(ValueError):
        criar_paciente(
            db_session,
            nome="Fulano",
            cpf="11144477735",
            cep="123"
        )


def test_aceita_cpf_com_mascara(db_session):
    criar_paciente(
        db_session,
        nome="João Souza",
        cpf="111.444.777-35",
        cep="01311-000"
    )

    pacientes = listar_pacientes(db_session)

    assert pacientes[0].cpf == "11144477735"


def test_lista_multiplos_pacientes(db_session):
    criar_paciente(
        db_session,
        nome="Maria Silva",
        cpf="11144477735",
        cep="01311000"
    )

    criar_paciente(
        db_session,
        nome="João Souza",
        cpf="52998224725",
        cep="20000000"
    )

    pacientes = listar_pacientes(db_session)

    assert len(pacientes) == 2

def test_busca_paciente_por_id(db_session):
    paciente = criar_paciente(
        db_session,
        nome="Maria Silva",
        cpf="11144477735",
        cep="01311000",
    )

    resultado = buscar_por_id(db_session, paciente.id)

    assert resultado is not None
    assert resultado.id == paciente.id
    assert resultado.nome == "Maria Silva"


def test_busca_paciente_inexistente_retorna_none(db_session):
    resultado = buscar_por_id(db_session, 9999)

    assert resultado is None


def test_remove_paciente_existente(db_session):
    paciente = criar_paciente(
        db_session,
        nome="Maria Silva",
        cpf="11144477735",
        cep="01311000",
    )

    resultado = remover_paciente(db_session, paciente.id)

    assert resultado is True
    assert buscar_por_id(db_session, paciente.id) is None


def test_remover_paciente_inexistente_retorna_false(db_session):
    resultado = remover_paciente(db_session, 9999)

    assert resultado is False
