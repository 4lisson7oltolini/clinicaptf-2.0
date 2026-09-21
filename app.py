import streamlit as st

from database.connection import SessionLocal
from database.initialization import inicializar_aplicacao
from services.auth_service import autenticar
from utils.accessibility import (
    aplicar_estilos_acessibilidade,
    inicializar_preferencias,
)
from utils.auth_guard import encerrar_sessao


# =========================================================
# Inicialização
# =========================================================

inicializar_aplicacao()
inicializar_preferencias()

st.set_page_config(
    page_title="Clínica PTF 2.0",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Tema visual — Clínica PTF 2.0
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       CORES
       ===================================================== */

    :root {
        color-scheme: light;

        --ptf-primary: #117C73;
        --ptf-primary-dark: #0D6861;
        --ptf-primary-light: #E7F4F2;

        --ptf-background: #F4F7FB;
        --ptf-surface: #FFFFFF;

        --ptf-text: #172033;
        --ptf-text-secondary: #64748B;

        --ptf-border: #E2E8F0;
    }


    /* =====================================================
       APLICAÇÃO
       ===================================================== */

    .stApp {
        background-color: #F4F7FB !important;
        color: #172033 !important;
    }

    .main {
        background-color: #F4F7FB !important;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background-color: #117C73 !important;
        border-right: none !important;
    }

    section[data-testid="stSidebar"] > div {
        background-color: #117C73 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.20) !important;
    }

    section[data-testid="stSidebar"] a {
        color: #FFFFFF !important;
        text-decoration: none !important;
    }

    section[data-testid="stSidebar"] a:hover {
        background-color: rgba(255, 255, 255, 0.10) !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] [aria-current="page"] {
        background-color: rgba(255, 255, 255, 0.16) !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] [aria-current="page"] * {
        color: #FFFFFF !important;
    }


    /* =====================================================
       BOTÃO DA SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.10) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }


    /* =====================================================
       TEXTOS
       ===================================================== */

    h1,
    h2,
    h3,
    h4 {
        color: #172033 !important;
    }

    p {
        color: #172033;
    }


    /* =====================================================
       INPUTS
       ===================================================== */

    div[data-baseweb="input"],
    div[data-baseweb="select"] > div,
    textarea {
        background-color: #FFFFFF !important;
        color: #172033 !important;
        border-color: #E2E8F0 !important;
    }

    input,
    textarea {
        color: #172033 !important;
        background-color: #FFFFFF !important;
    }

    input::placeholder,
    textarea::placeholder {
        color: #94A3B8 !important;
    }


    /* =====================================================
       SELECTBOX
       ===================================================== */

    div[data-baseweb="select"] span {
        color: #172033 !important;
    }


    /* =====================================================
       BOTÕES
       ===================================================== */

    .stButton > button {
        background-color: #117C73 !important;
        color: #FFFFFF !important;
        border: 1px solid #117C73 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    .stButton > button:hover {
        background-color: #0D6861 !important;
        border-color: #0D6861 !important;
        color: #FFFFFF !important;
    }


    /* =====================================================
       FORMULÁRIOS
       ===================================================== */

    div[data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
    }


    /* =====================================================
       CARDS / MÉTRICAS
       ===================================================== */

    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B !important;
    }

    div[data-testid="stMetricValue"] {
        color: #172033 !important;
    }


    /* =====================================================
       CONTAINERS
       ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-color: #E2E8F0 !important;
        border-radius: 12px !important;
    }


    /* =====================================================
       TABS
       ===================================================== */

    button[data-baseweb="tab"] {
        color: #64748B !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #117C73 !important;
    }

    div[data-baseweb="tab-highlight"] {
        background-color: #117C73 !important;
    }


    /* =====================================================
       ALERTAS
       ===================================================== */

    div[data-testid="stAlert"] {
        border-radius: 10px !important;
    }


    /* =====================================================
       DATAFRAME
       ===================================================== */

    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }


    /* =====================================================
       EXPANDERS
       ===================================================== */

    details {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }

    details summary {
        color: #172033 !important;
    }


    /* =====================================================
       SCROLLBAR
       ===================================================== */

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #F4F7FB;
    }

    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }


    /* =====================================================
       LOGIN
       ===================================================== */

    .ptf-login-wrapper {
        max-width: 460px;
        margin: 8vh auto 0 auto;
    }

    .ptf-login-header {
        text-align: center;
        margin-bottom: 30px;
    }

    .ptf-login-logo {
        width: 72px;
        height: 72px;
        margin: 0 auto 18px auto;

        display: flex;
        align-items: center;
        justify-content: center;

        background-color: #117C73;
        border-radius: 18px;

        font-size: 34px;
    }

    .ptf-login-title {
        color: #172033 !important;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .ptf-login-subtitle {
        color: #64748B !important;
        font-size: 0.95rem;
    }

    .ptf-login-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 28px;
        box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
    }


    /* =====================================================
       USUÁRIO DA SIDEBAR
       ===================================================== */

    .ptf-user-box {
        margin-top: 10px;
        margin-bottom: 15px;
        padding: 14px;
        border-radius: 10px;

        background-color: rgba(255, 255, 255, 0.08);

        border: 1px solid rgba(255, 255, 255, 0.10);
    }

    .ptf-user-name {
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .ptf-user-profile {
        font-size: 0.82rem;
        opacity: 0.80;
    }


    /* =====================================================
       SUBTÍTULO DAS PÁGINAS
       ===================================================== */

    .ptf-page-subtitle {
        color: #64748B !important;
        margin-top: -10px;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

aplicar_estilos_acessibilidade()


# =========================================================
# Estado da sessão
# =========================================================

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None


# =========================================================
# Tela de login
# =========================================================

def tela_login():
    """Exibe a tela de autenticação."""

    st.markdown(
        '<div class="ptf-login-wrapper">',
        unsafe_allow_html=True,
    )

    # ATENÇÃO: sem linhas em branco entre as divs aninhadas — <div> (ao
    # contrário de <style>) é interrompido pela primeira linha em branco
    # que aparecer dentro dele, e o resto vira bloco de código em vez de
    # HTML. Cada tag fica na própria linha, mas nenhuma linha vazia entre
    # elas.
    st.markdown(
        """
        <div class="ptf-login-header">
            <div class="ptf-login-logo">
                🩺
            </div>
            <div class="ptf-login-title">
                Clínica PTF 2.0
            </div>
            <div class="ptf-login-subtitle">
                Sistema de Gestão
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ptf-login-card">',
        unsafe_allow_html=True,
    )

    with st.form("login"):

        username = st.text_input(
            "Usuário",
            placeholder="Digite seu usuário",
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha",
        )

        enviado = st.form_submit_button(
            "Entrar",
            use_container_width=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
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

            profissional_id = (
                usuario.profissional.id
                if usuario and usuario.profissional
                else None
            )

        finally:

            db.close()

        if usuario:

            st.session_state["usuario"] = {
                "id": usuario.id,
                "nome": usuario.nome_completo,
                "perfil": usuario.perfil,
                "profissional_id": profissional_id,
            }

            st.rerun()

        else:

            st.error(
                "Usuário ou senha inválidos."
            )


# =========================================================
# Controle da tela de login
# =========================================================

if st.session_state["usuario"] is None:

    st.markdown(
        """
        <style>

        [data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    tela_login()

    st.stop()


# =========================================================
# Usuário autenticado
# =========================================================

usuario = st.session_state["usuario"]


# =========================================================
# Páginas
# =========================================================

pagina_inicio = st.Page(
    "pages/0_Inicio.py",
    title="Início",
    icon=":material/home:",
    default=True,
)


pagina_pacientes = st.Page(
    "pages/1_Pacientes.py",
    title="Pacientes",
    icon=":material/person:",
)


pagina_profissionais = st.Page(
    "pages/2_Profissionais.py",
    title="Profissionais",
    icon=":material/medical_services:",
)


pagina_agenda = st.Page(
    "pages/3_Agenda.py",
    title="Agenda",
    icon=":material/calendar_month:",
)


pagina_configuracoes = st.Page(
    "pages/5_Configuracoes.py",
    title="Configurações",
    icon=":material/settings:",
)


pagina_relatorios = st.Page(
    "pages/6_Relatorios.py",
    title="Relatórios",
    icon=":material/assessment:",
)


paginas_principais = [
    pagina_inicio,
    pagina_agenda,
    pagina_relatorios,
    pagina_configuracoes,
]

if usuario["perfil"] in {"admin", "atendente"}:
    paginas_principais.insert(1, pagina_pacientes)

if usuario["perfil"] == "admin":
    paginas_principais.insert(2, pagina_profissionais)

navegacao = st.navigation(
    {"Principal": paginas_principais},
    position="hidden",
)


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    # Mesma correção: sem linhas em branco entre as <div> aninhadas.
    st.markdown(
        """
        <div style="text-align: center; padding: 10px 0 25px 0;">
            <div style="font-size: 34px; margin-bottom: 6px;">
                🩺
            </div>
            <div style="font-size: 1.15rem; font-weight: 700;">
                Clínica PTF 2.0
            </div>
            <div style="font-size: 0.75rem; opacity: 0.75;">
                Sistema de Gestão
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("**Principal**")

    st.page_link(pagina_inicio, label="Início", icon=":material/home:")
    if usuario["perfil"] in {"admin", "atendente"}:
        st.page_link(pagina_pacientes, label="Pacientes", icon=":material/person:")
    if usuario["perfil"] == "admin":
        st.page_link(pagina_profissionais, label="Profissionais", icon=":material/medical_services:")
    st.page_link(pagina_agenda, label="Agenda", icon=":material/calendar_month:")
    st.page_link(pagina_relatorios, label="Relatórios", icon=":material/assessment:")
    st.page_link(pagina_configuracoes, label="Configurações", icon=":material/settings:")

    st.divider()

    st.markdown(
        f"""
        <div class="ptf-user-box">
            <div class="ptf-user-name">
                {usuario["nome"]}
            </div>
            <div class="ptf-user-profile">
                Perfil: {usuario["perfil"].capitalize()}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button(
        "Sair",
        use_container_width=True,
    ):

        encerrar_sessao()

        st.rerun()


# =========================================================
# Executar
# =========================================================

navegacao.run()