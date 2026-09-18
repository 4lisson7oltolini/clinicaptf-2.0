import streamlit as st


TEMAS = ("Claro", "Escuro")
NIVEIS_CONTRASTE = ("Padrão", "Alto", "Máximo")


def inicializar_preferencias() -> None:
    st.session_state.setdefault("ptf_tema", "Claro")
    st.session_state.setdefault("ptf_contraste", "Padrão")


def aplicar_estilos_acessibilidade() -> None:
    tema = st.session_state.get("ptf_tema", "Claro")
    contraste = st.session_state.get("ptf_contraste", "Padrão")

    if tema == "Escuro":
        fundo = "#0F172A"
        superficie = "#1E293B"
        texto = {
            "Padrão": "#E2E8F0",
            "Alto": "#F1F5F9",
            "Máximo": "#FFFFFF",
        }[contraste]
        texto_secundario = "#CBD5E1"
        borda = "#475569"
        placeholder = "#CBD5E1"
    else:
        fundo = "#F4F7FB"
        superficie = "#FFFFFF"
        texto = {
            "Padrão": "#172033",
            "Alto": "#0F172A",
            "Máximo": "#000000",
        }[contraste]
        texto_secundario = {
            "Padrão": "#64748B",
            "Alto": "#334155",
            "Máximo": "#172033",
        }[contraste]
        borda = "#CBD5E1"
        placeholder = "#64748B"

    st.markdown(
        f"""
        <style>
        :root {{
            color-scheme: {tema.lower()};
            --primary-color: #117C73;
            --background-color: {fundo};
            --secondary-background-color: {superficie};
            --text-color: {texto};
            --st-color-primary: #117C73;
            --st-color-background: {fundo};
            --st-color-bg-secondary: {superficie};
            --st-color-text: {texto};
            --ptf-background: {fundo};
            --ptf-surface: {superficie};
            --ptf-text: {texto};
            --ptf-text-secondary: {texto_secundario};
            --ptf-border: {borda};
        }}

        .stApp,
        .main,
        [data-testid="stAppViewContainer"] {{
            background-color: {fundo} !important;
            color: {texto} !important;
        }}

        h1, h2, h3, h4, h5, h6,
        p,
        label,
        [data-testid="stMarkdownContainer"] {{
            color: {texto} !important;
        }}

        [data-testid="stCaptionContainer"],
        [data-testid="stMetricLabel"],
        .ptf-page-subtitle {{
            color: {texto_secundario} !important;
        }}

        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        textarea,
        input,
        select {{
            background-color: {superficie} !important;
            color: {texto} !important;
            border-color: {borda} !important;
        }}

        input::placeholder,
        textarea::placeholder {{
            color: {placeholder} !important;
        }}

        div[data-baseweb="select"] span,
        div[data-testid="stMetric"],
        div[data-testid="stForm"],
        div[data-testid="stVerticalBlockBorderWrapper"],
        details {{
            background-color: {superficie} !important;
            color: {texto} !important;
            border-color: {borda} !important;
        }}

        div[data-testid="stMetricValue"],
        details summary {{
            color: {texto} !important;
        }}

        button[data-baseweb="tab"] {{
            color: {texto_secundario} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
