import streamlit as st

from database.connection import SessionLocal
from database.initialization import inicializar_aplicacao
from services.auth_service import autenticar


# ---------------------------------------------------------
# Inicialização
# ---------------------------------------------------------

inicializar_aplicacao()

st.set_page_config(
    page_title="Clínica PTF 2.0",
    page_icon="🩺",
    layout="wide",
)


# ---------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None


# ---------------------------------------------------------
# Tela de login
# ---------------------------------------------------------

def tela_login():
    """Exibe a tela de autenticação do sistema."""

    # Espaço superior
    st.write("")

    # Centraliza o card
    coluna_esquerda, coluna_login, coluna_direita = st.columns(
        [1, 1.2, 1]
    )

    with coluna_login:

        st.markdown(
            """
            <div style="
                text-align: center;
                margin-bottom: 25px;
            ">
                <h1 style="margin-bottom: 5px;">
                    Clínica PTF
                </h1>
                <p style="
                    color: #9CA3AF;
                    margin-top: 0;
                ">
                    Sistema de Gestão
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login"):

            username = st.text_input(
                "Usuário"
            )

            senha = st.text_input(
                "Senha",
                type="password",
            )

            enviado = st.form_submit_button(
                "Entrar",
                use_container_width=True,
            )

        if enviado:

            if not username or not senha:
                st.warning(
                    "Informe o usuário e a senha."
                )
                return

            db = SessionLocal()

            try:
                usuario = autenticar(
                    db,
                    username,
                    senha,
                )
            finally:
                db.close()

            if usuario:

                st.session_state["usuario"] = {
                    "id": usuario.id,
                    "nome": usuario.nome_completo,
                }

                st.rerun()

            else:
                st.error(
                    "Usuário ou senha inválidos."
                )
# ---------------------------------------------------------
# Controle da tela de login
# ---------------------------------------------------------

if st.session_state["usuario"] is None:

    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }

            [data-testid="collapsedControl"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    tela_login()

    st.stop()


# ---------------------------------------------------------
# Usuário autenticado
# ---------------------------------------------------------

with st.sidebar:

    st.markdown(
        f"**Usuário:** {st.session_state['usuario']['nome']}"
    )

    st.divider()

    if st.button(
        "Sair",
        use_container_width=True,
    ):
        st.session_state["usuario"] = None
        st.rerun()


# ---------------------------------------------------------
# Navegação
# ---------------------------------------------------------

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