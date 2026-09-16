import streamlit as st
from datetime import date

from database.connection import SessionLocal
from services.consulta_service import listar_consultas_do_dia
from utils.auth_guard import exigir_login


exigir_login()


st.title("Início")

st.caption(
    f"Visão geral da clínica — {date.today().strftime('%d/%m/%Y')}"
)


db = SessionLocal()

try:
    consultas_hoje = listar_consultas_do_dia(
        db,
        date.today(),
    )

    total_consultas = len(consultas_hoje)

    confirmadas = sum(
        1
        for consulta in consultas_hoje
        if consulta.status == "confirmada"
    )

    agendadas = sum(
        1
        for consulta in consultas_hoje
        if consulta.status == "agendada"
    )

    concluidas = sum(
        1
        for consulta in consultas_hoje
        if consulta.status == "concluida"
    )

finally:
    db.close()


coluna1, coluna2, coluna3, coluna4 = st.columns(4)


with coluna1:
    st.metric(
        "Consultas hoje",
        total_consultas,
    )


with coluna2:
    st.metric(
        "Agendadas",
        agendadas,
    )


with coluna3:
    st.metric(
        "Confirmadas",
        confirmadas,
    )


with coluna4:
    st.metric(
        "Concluídas",
        concluidas,
    )


st.divider()


st.subheader("Agenda de hoje")


if consultas_hoje:
    st.dataframe(
        [
            {
                "Horário": consulta.data_hora.strftime(
                    "%H:%M"
                ),
                "Paciente": consulta.paciente.nome,
                "Profissional": consulta.profissional.nome,
                "Status": consulta.status.capitalize(),
            }
            for consulta in consultas_hoje
        ],
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "Não existem consultas agendadas para hoje."
    )
