"""
Ponto de entrada do Streamlit.

Responsável pelo login do usuário e pela navegação
entre as páginas da aplicação.

A estrutura do banco de dados é gerenciada pelo Alembic.
"""

import streamlit as st

from database.connection import SessionLocal
from services.auth_service import autenticar


st.set_page_config(
    page_title="ClinicaPTF 2.0",
    page_icon="🩺",
    layout="wide",
)

if "usuario" not in st.session_state:
    st.session_state.usuario = None


def tela_login():
    """Exibe a tela de autenticação do sistema."""

    st.title("🩺 ClinicaPTF 2.0 — Login")

    with st.form("login"):
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        enviado = st.form_submit_button("Entrar")

    if enviado:
        db = SessionLocal()

        try:
            usuario = autenticar(db, username, senha)
        finally:
            db.close()

        if usuario:
            st.session_state.usuario = {
                "id": usuario.id,
                "nome": usuario.nome_completo,
            }

            st.rerun()

        else:
            st.error("Usuário ou senha inválidos.")


if st.session_state.usuario is None:
    tela_login()
    st.stop()


# ---------------------------------------------------------
# A partir daqui o usuário está autenticado
# ---------------------------------------------------------

with st.sidebar:
    st.markdown(f"👋 **{st.session_state.usuario['nome']}**")

    if st.button("Sair"):
        st.session_state.usuario = None
        st.rerun()

    st.divider()


pagina_inicio = st.Page(
    "pages/0_Inicio.py",
    title="Início",
    icon="🏠",
    default=True,
)

pagina_pacientes = st.Page(
    "pages/1_Pacientes.py",
    title="Pacientes",
    icon="👤",
)

pagina_profissionais = st.Page(
    "pages/2_Profissionais.py",
    title="Profissionais",
    icon="🩺",
)

pagina_agenda = st.Page(
    "pages/3_Agenda.py",
    title="Agenda",
    icon="📅",
)


navegacao = st.navigation(
    [
        pagina_inicio,
        pagina_pacientes,
        pagina_profissionais,
        pagina_agenda,
    ]
)

navegacao.run()
