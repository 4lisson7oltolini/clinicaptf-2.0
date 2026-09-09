"""
Ponto de entrada do Streamlit.
Responsabilidade única: configurar a página e delegar para pages/ e services/.
"""
import streamlit as st

from database.connection import SessionLocal, init_db
from services.paciente_service import criar_paciente, listar_pacientes, PacienteJaExisteError

st.set_page_config(page_title="ClinicaPTF 2.0", page_icon="🩺", layout="wide")

init_db()

st.title("🩺 ClinicaPTF 2.0")

with st.form("novo_paciente", clear_on_submit=True):
    st.subheader("Novo paciente")
    nome = st.text_input("Nome")
    cpf = st.text_input("CPF")
    cep = st.text_input("CEP")
    telefone = st.text_input("Telefone (opcional)")
    enviado = st.form_submit_button("Cadastrar")

if enviado:
    db = SessionLocal()
    try:
        criar_paciente(db, nome=nome, cpf=cpf, cep=cep, telefone=telefone or None)
        st.success(f"Paciente {nome} cadastrado com sucesso.")
    except (ValueError, PacienteJaExisteError) as erro:
        st.error(str(erro))
    finally:
        db.close()

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