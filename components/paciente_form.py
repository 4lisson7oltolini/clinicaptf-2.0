"""
Componentes de UI reutilizáveis entre páginas (evita duplicar formulários).
"""
import streamlit as st

from services.paciente_service import criar_paciente, PacienteJaExisteError


def formulario_novo_paciente(db_session_factory):
    """Renderiza o formulário de cadastro de paciente. Retorna True se cadastrou com sucesso."""
    with st.form("novo_paciente", clear_on_submit=True):
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        cep = st.text_input("CEP")
        telefone = st.text_input("Telefone (opcional)")
        enviado = st.form_submit_button("Cadastrar")

    if not enviado:
        return False

    db = db_session_factory()
    try:
        criar_paciente(db, nome=nome, cpf=cpf, cep=cep, telefone=telefone or None)
        st.success(f"Paciente {nome} cadastrado com sucesso.")
        return True
    except (ValueError, PacienteJaExisteError) as erro:
        st.error(str(erro))
        return False
    finally:
        db.close()