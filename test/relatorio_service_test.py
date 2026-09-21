from datetime import date, datetime
from types import SimpleNamespace

from services.relatorio_service import (
    gerar_csv,
    gerar_pdf,
    listar_consultas_periodo,
    montar_linhas_consultas,
    obter_intervalo_periodo,
)
from services.consulta_service import agendar_consulta
from services.paciente_service import criar_paciente
from services.profissional_service import criar_profissional


def test_obter_intervalos_de_periodo():
    referencia = date(2026, 9, 16)

    inicio, fim = obter_intervalo_periodo(referencia, "Dia")
    assert inicio.date() == date(2026, 9, 16)
    assert fim.date() == date(2026, 9, 17)

    inicio, fim = obter_intervalo_periodo(referencia, "Semana")
    assert inicio.date() == date(2026, 9, 14)
    assert fim.date() == date(2026, 9, 21)

    inicio, fim = obter_intervalo_periodo(referencia, "Mês")
    assert inicio.date() == date(2026, 9, 1)
    assert fim.date() == date(2026, 10, 1)

    inicio, fim = obter_intervalo_periodo(referencia, "Ano")
    assert inicio.date() == date(2026, 1, 1)
    assert fim.date() == date(2027, 1, 1)

    inicio, fim = obter_intervalo_periodo(
        date(2026, 12, 15),
        "Mês",
    )
    assert inicio.date() == date(2026, 12, 1)
    assert fim.date() == date(2027, 1, 1)


def test_listar_consultas_periodo_filtra_profissional_e_paciente(
    db_session,
):
    paciente1 = criar_paciente(
        db_session,
        nome="Maria Silva",
        cpf="11144477735",
        cep="01311000",
    )
    paciente2 = criar_paciente(
        db_session,
        nome="João Silva",
        cpf="52998224725",
        cep="01311000",
    )
    profissional1 = criar_profissional(
        db_session,
        nome="Dr. Carlos",
        especialidade="Cardiologia",
        registro_profissional="CRM-11111",
    )
    profissional2 = criar_profissional(
        db_session,
        nome="Dra. Ana",
        especialidade="Ortopedia",
        registro_profissional="CRM-22222",
    )

    agendar_consulta(
        db_session,
        paciente1.id,
        profissional1.id,
        datetime(2026, 9, 16, 9, 0),
    )
    agendar_consulta(
        db_session,
        paciente2.id,
        profissional2.id,
        datetime(2026, 9, 16, 11, 0),
    )

    consultas = listar_consultas_periodo(
        db_session,
        date(2026, 9, 16),
        "Dia",
        profissional_id=profissional1.id,
        paciente_id=paciente1.id,
    )

    assert len(consultas) == 1
    assert consultas[0].paciente_id == paciente1.id


def test_montar_linhas_consultas_usa_status_desconhecido_e_observacao_vazia(
    db_session,
):
    consulta = SimpleNamespace(
        data_hora=datetime(2026, 9, 16, 9, 0),
        paciente=SimpleNamespace(nome="Maria Silva"),
        profissional=SimpleNamespace(nome="Dr. Carlos"),
        status="status_novo",
        observacoes=None,
    )

    linhas = montar_linhas_consultas([consulta])

    assert linhas == [[
        "16/09/2026",
        "09:00",
        "Maria Silva",
        "Dr. Carlos",
        "status_novo",
        "",
    ]]


def test_gerar_csv_com_bom_utf8():
    conteudo = gerar_csv(
        ["Paciente", "Status"],
        [["João & Silva", "Concluída"]],
    )

    assert conteudo.startswith(bytes([239, 187, 191]))
    assert "João" in conteudo.decode("utf-8-sig")


def test_gerar_pdf():
    conteudo = gerar_pdf(
        "Histórico do paciente",
        "Período: Mês",
        ["Paciente", "Observações"],
        [["João & Silva", "Retorno <urgente>"]],
    )

    assert conteudo.startswith(b"%PDF")


def test_gerar_pdf_sem_linhas():
    conteudo = gerar_pdf(
        "Relatório vazio",
        "Sem registros",
        ["Paciente", "Status"],
        [],
    )

    assert conteudo.startswith(b"%PDF")