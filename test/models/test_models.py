import pytest

from models.consulta import Consulta
from models.paciente import Paciente
from models.profissional import Profissional
from models.usuario import Usuario


def test_model_paciente_valida_cpf_e_cep_ao_atribuir():
    paciente = Paciente(
        nome="Maria Silva",
        cpf="529.982.247-25",
        cep="01311-000",
    )

    assert paciente.cpf == "52998224725"
    assert paciente.cep == "01311000"


def test_model_paciente_rejeita_cpf_invalido():
    with pytest.raises(ValueError, match="CPF inválido"):
        Paciente(
            nome="Maria Silva",
            cpf="11111111111",
            cep="01311000",
        )


def test_model_paciente_rejeita_cep_invalido():
    with pytest.raises(ValueError, match="CEP inválido"):
        Paciente(
            nome="Maria Silva",
            cpf="52998224725",
            cep="123",
        )


def test_repr_dos_models_identifica_entidades():
    paciente = Paciente(id=1, nome="Maria Silva", cpf="52998224725", cep="01311000")
    profissional = Profissional(
        id=2,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-1",
    )
    usuario = Usuario(
        id=3,
        username="carlos",
        senha_hash="hash",
        nome_completo="Carlos Mendes",
        perfil="profissional",
    )
    consulta = Consulta(
        id=4,
        paciente_id=1,
        profissional_id=2,
        data_hora=None,
    )

    assert repr(paciente) == "<Paciente id=1 nome='Maria Silva'>"
    assert repr(profissional) == "<Profissional id=2 nome='Dr. Carlos Mendes'>"
    assert "id=3" in repr(usuario)
    assert "username='carlos'" in repr(usuario)
    assert "id=4" in repr(consulta)
