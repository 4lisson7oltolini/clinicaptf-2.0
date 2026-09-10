from datetime import datetime, date, time

import streamlit as st

from database.connection import SessionLocal
from services.paciente_service import listar_pacientes
from services.profissional_service import listar_profissionais
from services.consulta_service import agendar_consulta, listar_consultas, ConflitoDeHorarioError
from utils.auth_guard import exigir_login

exigir_login()

st.title("📅 Agenda")

db = SessionLocal()
try:
    pacientes = listar_pacientes(db)
    profissionais = listar_profissionais(db)
finally:
    db.close()

if not pacientes or not profissionais:
    st.warning("Cadastre ao menos um paciente e um profissional antes de agendar.")
else:
    with st.form("nova_consulta", clear_on_submit=True):
        paciente = st.selectbox("Paciente", pacientes, format_func=lambda p: p.nome)
        profissional = st.selectbox("Profissional", profissionais, format_func=lambda p: p.nome)
        data = st.date_input("Data", value=date.today())
        hora = st.time_input("Hora", value=time(9, 0))
        observacoes = st.text_area("Observações (opcional)")
        enviado = st.form_submit_button("Agendar")

    if enviado:
        db = SessionLocal()
        try:
            agendar_consulta(
                db,
                paciente_id=paciente.id,
                profissional_id=profissional.id,
                data_hora=datetime.combine(data, hora),
                observacoes=observacoes or None,
            )
            st.success("Consulta agendada com sucesso.")
        except ConflitoDeHorarioError as erro:
            st.error(str(erro))
        finally:
            db.close()

st.subheader("Consultas agendadas")
db = SessionLocal()
try:
    consultas = listar_consultas(db)
    if consultas:
        st.dataframe(
            [
                {
                    "Paciente": c.paciente.nome,
                    "Profissional": c.profissional.nome,
                    "Data/Hora": c.data_hora,
                    "Status": c.status,
                }
                for c in consultas
            ],
            use_container_width=True,
        )
    else:
        st.info("Nenhuma consulta agendada ainda.")
finally:
    db.close()