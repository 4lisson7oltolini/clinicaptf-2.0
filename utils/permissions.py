from utils.auth_guard import obter_usuario_autenticado


def usuario_e_admin() -> bool:
    usuario = obter_usuario_autenticado()
    return usuario.get("perfil") == "admin"


def usuario_e_profissional() -> bool:
    usuario = obter_usuario_autenticado()
    return usuario.get("perfil") == "profissional"


def exigir_admin() -> None:
    usuario = obter_usuario_autenticado()

    if usuario.get("perfil") != "admin":
        import streamlit as st

        st.error(
            "Você não possui permissão para acessar esta página."
        )
        st.stop()