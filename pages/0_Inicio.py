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

exigir_login()

st.title("🏠 Início")
st.markdown(f"Bem-vindo(a), **{st.session_state.usuario['nome']}**.")

db = SessionLocal()
try:
    consultas_hoje = listar_consultas_do_dia(db)
    profissionais = listar_profissionais(db)
    disponiveis_agora = [p for p in profissionais if not profissional_ocupado_agora(db, p.id)]
    total_consultas = contar_consultas_ativas(db)
finally:
    db.close()

col1, col2, col3 = st.columns(3)
col1.metric("Consultas hoje", len(consultas_hoje))
col2.metric("Médicos disponíveis agora", len(disponiveis_agora))
col3.metric("Consultas marcadas (total)", total_consultas)

st.subheader("📋 Consultas de hoje")
if consultas_hoje:
    st.dataframe(
        [
            {
                "Horário": c.data_hora.strftime("%H:%M"),
                "Paciente": c.paciente.nome,
                "Profissional": c.profissional.nome,
                "Status": c.status,
            }
            for c in consultas_hoje
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Nenhuma consulta marcada para hoje.")

st.subheader("🩺 Médicos disponíveis agora")
if disponiveis_agora:
    st.dataframe(
        [{"Nome": p.nome, "Especialidade": p.especialidade} for p in disponiveis_agora],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Nenhum profissional disponível neste momento.")
