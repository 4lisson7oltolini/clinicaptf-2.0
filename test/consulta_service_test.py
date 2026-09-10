from datetime import datetime, timedelta

import pytest

from services.paciente_service import criar_paciente
from services.profissional_service import criar_profissional
from services.consulta_service import (
    agendar_consulta,
    ConflitoDeHorarioError,
    listar_consultas_do_dia,
    contar_consultas_ativas,
    profissional_ocupado_agora,
)


@pytest.fixture()
def paciente_e_profissional(db_session):
    paciente = criar_paciente(db_session, nome="Maria Silva", cpf="11144477735", cep="01311000")
    profissional = criar_profissional(
        db_session, nome="Dr. João", especialidade="Fisioterapia Ortopédica", registro_profissional="CREFITO-12345"
    )
    return paciente, profissional


def test_agenda_consulta_com_sucesso(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session, paciente_id=paciente.id, profissional_id=profissional.id, data_hora=datetime(2026, 10, 1, 14, 0)
    )

    assert consulta.status == "agendada"


def test_bloqueia_conflito_de_horario(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 14, 0))

    with pytest.raises(ConflitoDeHorarioError):
        agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 14, 20))


def test_lista_apenas_consultas_do_dia_informado(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional
    hoje = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    amanha = hoje + timedelta(days=1)

    agendar_consulta(db_session, paciente.id, profissional.id, hoje)
    agendar_consulta(db_session, paciente.id, profissional.id, amanha)

    consultas_de_hoje = listar_consultas_do_dia(db_session, dia=hoje.date())

    assert len(consultas_de_hoje) == 1
    assert consultas_de_hoje[0].data_hora.date() == hoje.date()


def test_conta_apenas_consultas_nao_canceladas(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 9, 0))
    agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 11, 0))

    assert contar_consultas_ativas(db_session) == 2


def test_profissional_ocupado_agora_quando_ha_consulta_no_horario_atual(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime.now())

    assert profissional_ocupado_agora(db_session, profissional.id) is True


def test_profissional_livre_agora_quando_nao_ha_consulta_proxima(db_session, paciente_e_profissional):
    _, profissional = paciente_e_profissional

    assert profissional_ocupado_agora(db_session, profissional.id) is False

def test_nao_permite_status_invalido(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    with pytest.raises(ValueError):
        consulta.status = "qualquer_status"


def test_consulta_possui_paciente_e_profissional(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    assert consulta.paciente.id == paciente.id
    assert consulta.profissional.id == profissional.id