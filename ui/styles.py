import streamlit as st


def aplicar_estilos():
    st.markdown(
        """
        <style>

        /* ==============================
           GERAL
        ============================== */

        .stApp {
            background-color: #f5f7fb;
        }

        .main .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }


        /* ==============================
           SIDEBAR
        ============================== */

        [data-testid="stSidebar"] {
            background-color: #0f766e;
        }

        [data-testid="stSidebar"] * {
            color: white;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: white;
        }


        /* ==============================
           TÍTULOS
        ============================== */

        h1 {
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #172033;
        }

        h2 {
            font-weight: 650;
            color: #172033;
        }

        h3 {
            font-weight: 600;
            color: #263247;
        }


        /* ==============================
           CARDS
        ============================== */

        div[data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748b;
        }

        div[data-testid="stMetricValue"] {
            color: #172033;
            font-weight: 700;
        }


        /* ==============================
           BOTÕES
        ============================== */

        .stButton > button {
            border-radius: 8px;
            min-height: 42px;
            font-weight: 600;
        }


        /* ==============================
           INPUTS
        ============================== */

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 8px;
        }


        /* ==============================
           EXPANDERS
        ============================== */

        .streamlit-expanderHeader {
            font-weight: 600;
        }


        /* ==============================
           TABELAS
        ============================== */

        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
        }


        /* ==============================
           DIVISORES
        ============================== */

        hr {
            border-color: #e5e7eb;
        }


        /* ==============================
           RESPONSIVIDADE
        ============================== */

        @media (max-width: 900px) {

            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )
