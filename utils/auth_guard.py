"""
Guarda de autenticação: cada página em pages/ chama isso no topo.
Sem essa checagem, o Streamlit deixa acessar qualquer página direto pela URL,
ignorando o login feito em app.py.
"""
import streamlit as st


def exigir_login():
    if st.session_state.get("usuario") is None:
        st.warning("Faça login na página inicial para continuar.")
        st.stop()