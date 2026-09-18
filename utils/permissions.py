from utils.auth_guard import obter_usuario_autenticado


def usuario_e_admin() -> bool:
    usuario = obter_usuario_autenticado()
    return usuario.get("perfil") == "admin"


def usuario_e_profissional() -> bool:
    usuario = obter_usuario_autenticado()
    return usuario.get("perfil") == "profissional"


def usuario_e_atendente() -> bool:
    usuario = obter_usuario_autenticado()
    return usuario.get("perfil") == "atendente"


def usuario_tem_perfil(*perfis: str) -> bool:
    usuario = obter_usuario_autenticado()
    return usuario.get("perfil") in perfis


def exigir_admin() -> None:
    usuario = obter_usuario_autenticado()

    if usuario.get("perfil") != "admin":
        import streamlit as st

        st.error(
            "Você não possui permissão para acessar esta página."
        )
        st.stop()


def exigir_perfil(*perfis: str) -> None:
    """Interrompe a página quando o perfil atual não é permitido."""

    if not usuario_tem_perfil(*perfis):
        import streamlit as st

        st.error(
            "Você não possui permissão para acessar esta página."
        )
        st.stop()