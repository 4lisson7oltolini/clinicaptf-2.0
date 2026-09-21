from __future__ import annotations

from datetime import date, datetime, time, timedelta
from io import BytesIO, StringIO
import csv
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session, joinedload

from models.consulta import Consulta


TIPOS_PERIODO = {
    "Dia": "dia",
    "Semana": "semana",
    "Mês": "mes",
    "Ano": "ano",
}

STATUS_LABELS = {
    "agendada": "Agendada",
    "confirmada": "Confirmada",
    "concluida": "Concluída",
    "cancelada": "Cancelada",
}


def obter_intervalo_periodo(
    referencia: date,
    periodo: str,
) -> tuple[datetime, datetime]:
    """Retorna o intervalo inclusivo do período selecionado."""

    inicio = referencia

    if periodo == "Semana":
        inicio = referencia - timedelta(days=referencia.weekday())
        fim = inicio + timedelta(days=7)
    elif periodo == "Mês":
        inicio = referencia.replace(day=1)
        if inicio.month == 12:
            fim = inicio.replace(
                year=inicio.year + 1,
                month=1,
            )
        else:
            fim = inicio.replace(month=inicio.month + 1)
    elif periodo == "Ano":
        inicio = referencia.replace(month=1, day=1)
        fim = inicio.replace(year=inicio.year + 1)
    else:
        fim = inicio + timedelta(days=1)

    return (
        datetime.combine(inicio, time.min),
        datetime.combine(fim, time.min),
    )


def listar_consultas_periodo(
    db: Session,
    referencia: date,
    periodo: str,
    profissional_id: int | None = None,
    paciente_id: int | None = None,
) -> list[Consulta]:
    inicio, fim = obter_intervalo_periodo(referencia, periodo)

    query = (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
        .filter(
            Consulta.data_hora >= inicio,
            Consulta.data_hora < fim,
        )
    )

    if profissional_id is not None:
        query = query.filter(Consulta.profissional_id == profissional_id)

    if paciente_id is not None:
        query = query.filter(Consulta.paciente_id == paciente_id)

    return query.order_by(Consulta.data_hora).all()


def montar_linhas_consultas(consultas: list[Consulta]) -> list[list[str]]:
    return [
        [
            consulta.data_hora.strftime("%d/%m/%Y"),
            consulta.data_hora.strftime("%H:%M"),
            consulta.paciente.nome,
            consulta.profissional.nome,
            STATUS_LABELS.get(consulta.status, consulta.status),
            consulta.observacoes or "",
        ]
        for consulta in consultas
    ]


def gerar_csv(
    cabecalho: list[str],
    linhas: list[list[str]],
) -> bytes:
    arquivo = StringIO(newline="")
    escritor = csv.writer(arquivo, delimiter=";")
    escritor.writerow(cabecalho)
    escritor.writerows(linhas)
    return ("\ufeff" + arquivo.getvalue()).encode("utf-8")


def gerar_pdf(
    titulo: str,
    subtitulo: str,
    cabecalho: list[str],
    linhas: list[list[str]],
) -> bytes:
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloRelatorio",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=6,
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloRelatorio",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=14,
    )
    estilo_celula = ParagraphStyle(
        "CelulaRelatorio",
        parent=estilos["Normal"],
        fontSize=8,
        leading=10,
    )

    elementos = [
        Paragraph(titulo, estilo_titulo),
        Paragraph(subtitulo, estilo_subtitulo),
    ]

    tabela_dados = [
        [Paragraph(escape(str(item)), estilo_celula) for item in cabecalho],
        *[
            [Paragraph(escape(str(item)), estilo_celula) for item in linha]
            for linha in linhas
        ],
    ]

    if len(tabela_dados) == 1:
        tabela_dados.append(
            [Paragraph("Nenhum registro encontrado.", estilo_celula)]
            + [""] * (len(cabecalho) - 1)
        )

    tabela = Table(tabela_dados, repeatRows=1)
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#117C73")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                    colors.white,
                    colors.HexColor("#F4F7FB"),
                ]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elementos.append(tabela)
    documento.build(elementos)

    return buffer.getvalue()
