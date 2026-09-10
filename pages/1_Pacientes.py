import streamlit as st

from database.connection import SessionLocal
from services.paciente_service import listar_pacientes
from components.paciente_form import formulario_novo_paciente
from utils.auth_guard import exigir_login

exigir_login()

st.title("👤 Pacientes")

formulario_novo_paciente(SessionLocal)

st.subheader("Pacientes cadastrados")
db = SessionLocal()
try:
    pacientes = listar_pacientes(db)
    if pacientes:
        st.dataframe(
            [{"Nome": p.nome, "CPF": p.cpf, "CEP": p.cep, "Telefone": p.telefone} for p in pacientes],
            use_container_width=True,
        )
    else:
        st.info("Nenhum paciente cadastrado ainda.")
finally:
    db.close()