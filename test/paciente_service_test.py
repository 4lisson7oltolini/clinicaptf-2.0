import pytest

from services.paciente_service import criar_paciente, listar_pacientes, PacienteJaExisteError


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