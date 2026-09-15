"""
Guarda de autenticação da aplicação.

Responsabilidades:
- verificar se existe um usuário autenticado;
- impedir acesso a páginas protegidas;
- fornecer acesso aos dados do usuário autenticado;
- encerrar corretamente a sessão.
"""

import streamlit as st


CHAVE_USUARIO = "usuario"


def usuario_autenticado() -> bool:
    """
    Verifica se existe um usuário autenticado na sessão.

    Returns:
        True quando existe uma sessão válida.
        False caso contrário.
    """

    usuario = st.session_state.get(CHAVE_USUARIO)

    if not isinstance(usuario, dict):
        return False

    return bool(
        usuario.get("id")
        and usuario.get("nome")
    )


def exigir_login() -> None:
    """
    Impede o acesso à página quando o usuário não está autenticado.

    Deve ser chamada no início de cada página protegida.
    """

    if not usuario_autenticado():

        st.warning(
            "Faça login para acessar esta página."
        )

        st.stop()


def obter_usuario_autenticado() -> dict:
    """
    Retorna os dados do usuário autenticado.

    Returns:
        Dicionário contendo os dados da sessão.

    Raises:
        RuntimeError:
            Caso não exista um usuário autenticado.
    """

    exigir_login()

    return st.session_state[CHAVE_USUARIO]


def encerrar_sessao() -> None:
    """
    Encerra a sessão do usuário atual.

    A função remove explicitamente os dados de autenticação
    armazenados no session_state.
    """

    st.session_state[CHAVE_USUARIO] = None
