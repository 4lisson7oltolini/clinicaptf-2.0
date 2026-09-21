from datetime import date

import streamlit as st

from database.connection import SessionLocal
from services.paciente_service import listar_pacientes
from services.profissional_service import listar_profissionais
from services.relatorio_service import (
    STATUS_LABELS,
    TIPOS_PERIODO,
    gerar_csv,
    gerar_pdf,
    listar_consultas_periodo,
    montar_linhas_consultas,
)
from utils.auth_guard import exigir_login, obter_usuario_autenticado


exigir_login()
usuario = obter_usuario_autenticado()


st.title("Relatórios")
st.caption("Consulte e baixe os dados de atendimentos da clínica.")


TIPOS_RELATORIO = (
    "Agendamentos por período",
    "Histórico do paciente",
    "Histórico de atendimento por médico",
)

with st.container(border=True):
    tipo_relatorio = st.selectbox(
        "Tipo de relatório",
        TIPOS_RELATORIO,
    )

    periodo = st.selectbox(
        "Período",
        tuple(TIPOS_PERIODO),
    )

    referencia = st.date_input(
        "Data de referência",
        value=date.today(),
    )

    db = SessionLocal()
    try:
        pacientes = listar_pacientes(db)
        profissionais = listar_profissionais(db)
    finally:
        db.close()

    paciente_selecionado = None
    profissional_selecionado = None

    if tipo_relatorio == "Histórico do paciente":
        paciente_selecionado = st.selectbox(
            "Paciente",
            pacientes,
            format_func=lambda paciente: (
                f"{paciente.nome} - CPF: {paciente.cpf}"
            ),
        )

    if tipo_relatorio == "Histórico de atendimento por médico":
        if usuario.get("perfil") == "profissional":
            profissionais = [
                profissional
                for profissional in profissionais
                if profissional.id == usuario.get("profissional_id")
            ]

        profissional_selecionado = st.selectbox(
            "Profissional",
            profissionais,
            format_func=lambda profissional: (
                f"{profissional.nome} - {profissional.especialidade}"
            ),
        )

    gerar = st.button(
        "Gerar relatório",
        type="primary",
        use_container_width=True,
    )


if gerar:
    profissional_id = None
    paciente_id = None

    if usuario.get("perfil") == "profissional":
        profissional_id = usuario.get("profissional_id")

    if profissional_selecionado is not None:
        profissional_id = profissional_selecionado.id

    if paciente_selecionado is not None:
        paciente_id = paciente_selecionado.id

    db = SessionLocal()
    try:
        consultas = listar_consultas_periodo(
            db,
            referencia=referencia,
            periodo=periodo,
            profissional_id=profissional_id,
            paciente_id=paciente_id,
        )
    finally:
        db.close()

    linhas = montar_linhas_consultas(consultas)
    cabecalho = [
        "Data",
        "Horário",
        "Paciente",
        "Profissional",
        "Status",
        "Observações",
    ]
    titulo = tipo_relatorio
    subtitulo = (
        f"Período: {periodo} | Referência: "
        f"{referencia.strftime('%d/%m/%Y')} | "
        f"Registros: {len(linhas)}"
    )

    st.session_state["relatorio_dados"] = {
        "linhas": linhas,
        "cabecalho": cabecalho,
        "titulo": titulo,
        "subtitulo": subtitulo,
        "csv": gerar_csv(cabecalho, linhas),
        "pdf": gerar_pdf(titulo, subtitulo, cabecalho, linhas),
    }


relatorio = st.session_state.get("relatorio_dados")

if relatorio is not None:
    st.divider()
    st.subheader(relatorio["titulo"])
    st.caption(relatorio["subtitulo"])

    if relatorio["linhas"]:
        st.dataframe(
            [
                dict(zip(relatorio["cabecalho"], linha))
                for linha in relatorio["linhas"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nenhum registro encontrado para os filtros selecionados.")

    coluna_csv, coluna_pdf = st.columns(2)

    with coluna_csv:
        st.download_button(
            "Baixar CSV",
            data=relatorio["csv"],
            file_name="relatorio_clinica_ptf.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with coluna_pdf:
        st.download_button(
            "Baixar PDF",
            data=relatorio["pdf"],
            file_name="relatorio_clinica_ptf.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
