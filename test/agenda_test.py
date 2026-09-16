from datetime import datetime

from services.consulta_service import (
    agendar_consulta,
    cancelar_consulta,
    listar_consultas,
)


def test_agenda_lista_consultas_em_ordem_de_horario(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 15, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 12, 0),
    )

    consultas = listar_consultas(
        db_session,
        data=datetime(2026, 10, 1),
    )

    assert len(consultas) == 3

    assert consultas[0].data_hora.hour == 9
    assert consultas[1].data_hora.hour == 12
    assert consultas[2].data_hora.hour == 15


def test_agenda_filtra_por_data_e_profissional(
    db_session,
):
    from services.paciente_service import criar_paciente
    from services.profissional_service import criar_profissional

    paciente = criar_paciente(
        db_session,
        nome="Maria Silva",
        cpf="11144477735",
        cep="01311000",
    )

    profissional1 = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-11111",
    )

    profissional2 = criar_profissional(
        db_session,
        nome="Dra. Ana",
        especialidade="Fisioterapia Esportiva",
        registro_profissional="CREFITO-22222",
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional1.id,
        datetime(2026, 10, 1, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional2.id,
        datetime(2026, 10, 1, 10, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional1.id,
        datetime(2026, 10, 2, 9, 0),
    )

    consultas = listar_consultas(
        db_session,
        profissional_id=profissional1.id,
        data=datetime(2026, 10, 1),
    )

    assert len(consultas) == 1
    assert consultas[0].profissional_id == profissional1.id
    assert consultas[0].data_hora.date().isoformat() == "2026-10-01"


def test_agenda_mostra_canceladas_quando_filtro_ativado(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    cancelar_consulta(
        db_session,
        consulta.id,
    )

    consultas = listar_consultas(
        db_session,
        data=datetime(2026, 10, 1),
        incluir_canceladas=True,
    )

    assert len(consultas) == 1
    assert consultas[0].status == "cancelada"


def test_agenda_oculta_canceladas_por_padrao(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    cancelar_consulta(
        db_session,
        consulta.id,
    )

    consultas = listar_consultas(
        db_session,
        data=datetime(2026, 10, 1),
        incluir_canceladas=False,
    )

    assert consultas == []


def test_agenda_combina_filtro_de_profissional_data_e_canceladas(
    db_session,
):
    from services.paciente_service import criar_paciente
    from services.profissional_service import criar_profissional

    paciente = criar_paciente(
        db_session,
        nome="Carlos Souza",
        cpf="52998224725",
        cep="01311000",
    )

    profissional1 = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-33333",
    )

    profissional2 = criar_profissional(
        db_session,
        nome="Dra. Ana",
        especialidade="Ortopedia",
        registro_profissional="CREFITO-44444",
    )

    consulta1 = agendar_consulta(
        db_session,
        paciente.id,
        profissional1.id,
        datetime(2026, 10, 1, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional1.id,
        datetime(2026, 10, 1, 10, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional2.id,
        datetime(2026, 10, 1, 11, 0),
    )

    cancelar_consulta(
        db_session,
        consulta1.id,
    )

    consultas = listar_consultas(
        db_session,
        profissional_id=profissional1.id,
        data=datetime(2026, 10, 1),
        incluir_canceladas=False,
    )

    assert len(consultas) == 1
    assert consultas[0].profissional_id == profissional1.id
    assert consultas[0].status != "cancelada"
    assert consultas[0].data_hora.hour == 10