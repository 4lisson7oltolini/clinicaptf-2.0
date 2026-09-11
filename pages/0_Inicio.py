"""
Tela Início (dashboard): visão rápida do dia para quem abre o sistema pela manhã.
"""

import streamlit as st

from database.connection import SessionLocal
from services.profissional_service import listar_profissionais
from services.consulta_service import (
    listar_consultas_do_dia,
    contar_consultas_ativas,
    profissional_ocupado_agora,
)
from utils.auth_guard import exigir_login


# ---------------------------------------------------------
# Autenticação
# ---------------------------------------------------------

exigir_login()


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------

st.title("Início")

st.markdown(
    f"Bem-vindo(a), **{st.session_state['usuario']['nome']}**."
)


# ---------------------------------------------------------
# Dados do dashboard
# ---------------------------------------------------------

db = SessionLocal()

try:
    consultas_hoje = listar_consultas_do_dia(db)

    profissionais = listar_profissionais(db)

    disponiveis_agora = [
        profissional
        for profissional in profissionais
        if not profissional_ocupado_agora(
            db,
            profissional.id,
        )
    ]

    total_consultas = contar_consultas_ativas(db)

finally:
    db.close()


# ---------------------------------------------------------
# Indicadores
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Consultas hoje",
    len(consultas_hoje),
)

col2.metric(
    "Profissionais disponíveis agora",
    len(disponiveis_agora),
)

col3.metric(
    "Consultas marcadas",
    total_consultas,
)


# ---------------------------------------------------------
# Consultas de hoje
# ---------------------------------------------------------

st.subheader("Consultas de hoje")

if consultas_hoje:

    dados_consultas = [
        {
            "Horário": consulta.data_hora.strftime("%H:%M"),
            "Paciente": consulta.paciente.nome,
            "Profissional": consulta.profissional.nome,
            "Status": consulta.status,
        }
        for consulta in consultas_hoje
    ]

    st.dataframe(
        dados_consultas,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "Nenhuma consulta marcada para hoje."
    )


# ---------------------------------------------------------
# Profissionais disponíveis
# ---------------------------------------------------------

st.subheader("Profissionais disponíveis agora")

if disponiveis_agora:

    dados_profissionais = [
        {
            "Nome": profissional.nome,
            "Especialidade": profissional.especialidade,
        }
        for profissional in disponiveis_agora
    ]

    st.dataframe(
        dados_profissionais,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "Nenhum profissional disponível neste momento."
    )