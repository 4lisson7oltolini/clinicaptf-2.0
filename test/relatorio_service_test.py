from datetime import date

from services.relatorio_service import (
    gerar_csv,
    gerar_pdf,
    obter_intervalo_periodo,
)


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