from datetime import datetime

import pytest

from services.consulta_service import (
    ConflitoDeHorarioError,
    agendar_consulta,
    buscar_consulta_por_id,
    cancelar_consulta,
)


def test_fluxo_de_conflito_e_liberacao_de_horario(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional
    horario_inicial = datetime(2026, 10, 6, 9, 0)

    primeira_consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=horario_inicial,
    )

    db_session.expire_all()
    primeira_persistida = buscar_consulta_por_id(
        db_session,
        primeira_consulta.id,
    )
    assert primeira_persistida is not None
    assert primeira_persistida.status == "agendada"

    with pytest.raises(ConflitoDeHorarioError):
        agendar_consulta(
            db_session,
            paciente_id=paciente.id,
            profissional_id=profissional.id,
            data_hora=datetime(2026, 10, 6, 9, 20),
        )

    consulta_no_limite = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 6, 9, 50),
    )

    db_session.expire_all()
    consulta_no_limite_persistida = buscar_consulta_por_id(
        db_session,
        consulta_no_limite.id,
    )
    assert consulta_no_limite_persistida is not None
    assert consulta_no_limite_persistida.data_hora == datetime(
        2026,
        10,
        6,
        9,
        50,
    )

    consulta_cancelada = cancelar_consulta(
        db_session,
        primeira_persistida.id,
    )
    assert consulta_cancelada.status == "cancelada"

    db_session.expire_all()
    primeira_cancelada_persistida = buscar_consulta_por_id(
        db_session,
        primeira_persistida.id,
    )
    assert primeira_cancelada_persistida.status == "cancelada"

    consulta_horario_liberado = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=horario_inicial,
    )

    db_session.expire_all()
    consulta_horario_liberado_persistida = buscar_consulta_por_id(
        db_session,
        consulta_horario_liberado.id,
    )

    assert consulta_horario_liberado_persistida is not None
    assert consulta_horario_liberado_persistida.status == "agendada"
    assert consulta_horario_liberado_persistida.data_hora == horario_inicial
