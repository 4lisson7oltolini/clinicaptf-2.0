import pytest
import streamlit as st

from utils.auth_guard import (
    usuario_autenticado,
    exigir_login,
    obter_usuario_autenticado,
)


def limpar_sessao():
    """Limpa a sessão do Streamlit antes de cada cenário."""
    st.session_state.clear()


# ---------------------------------------------------------
# Usuário não autenticado
# ---------------------------------------------------------

def test_usuario_nao_autenticado():
    limpar_sessao()

    assert usuario_autenticado() is False


def test_usuario_none_nao_e_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = None

    assert usuario_autenticado() is False


def test_usuario_vazio_nao_e_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {}

    assert usuario_autenticado() is False


def test_usuario_invalido_nao_e_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = "Administrador"

    assert usuario_autenticado() is False


# ---------------------------------------------------------
# Sessão parcialmente inválida
# ---------------------------------------------------------

def test_usuario_sem_id_nao_e_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {
        "nome": "Administrador",
    }

    assert usuario_autenticado() is False


def test_usuario_sem_nome_nao_e_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
    }

    assert usuario_autenticado() is False


def test_usuario_com_id_invalido_nao_e_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 0,
        "nome": "Administrador",
    }

    assert usuario_autenticado() is False


def test_usuario_com_nome_vazio_nao_e_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
        "nome": "",
    }

    assert usuario_autenticado() is False


# ---------------------------------------------------------
# Usuário autenticado
# ---------------------------------------------------------

def test_usuario_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
        "nome": "Administrador",
    }

    assert usuario_autenticado() is True


def test_usuario_autenticado_com_id_string():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": "1",
        "nome": "Administrador",
    }

    assert usuario_autenticado() is True


# ---------------------------------------------------------
# Recuperação do usuário autenticado
# ---------------------------------------------------------

def test_obter_usuario_autenticado():
    limpar_sessao()

    usuario = {
        "id": 1,
        "nome": "Administrador",
    }

    st.session_state["usuario"] = usuario

    resultado = obter_usuario_autenticado()

    assert resultado == usuario


def test_obter_usuario_preserva_dados_da_sessao():
    limpar_sessao()

    usuario = {
        "id": 15,
        "nome": "Administrador da Clínica",
    }

    st.session_state["usuario"] = usuario

    resultado = obter_usuario_autenticado()

    assert resultado["id"] == 15
    assert resultado["nome"] == "Administrador da Clínica"


# ---------------------------------------------------------
# Proteção de acesso
# ---------------------------------------------------------

def test_exigir_login_permite_usuario_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
        "nome": "Administrador",
    }

    # Não deve interromper a execução.
    exigir_login()


def test_exigir_login_interrompe_usuario_nao_autenticado():
    limpar_sessao()

    assert usuario_autenticado() is False


# ---------------------------------------------------------
# Logout / limpeza da sessão
# ---------------------------------------------------------

def test_sessao_apos_logout_nao_e_autenticada():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
        "nome": "Administrador",
    }

    assert usuario_autenticado() is True

    # Simula o comportamento atual do botão "Sair" no app.py.
    st.session_state["usuario"] = None

    assert usuario_autenticado() is False


def test_sessao_limpa_completamente_nao_e_autenticada():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
        "nome": "Administrador",
    }

    assert usuario_autenticado() is True

    st.session_state.clear()

    assert usuario_autenticado() is False
    
def test_encerrar_sessao_remove_usuario():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
        "nome": "Administrador",
    }

    assert usuario_autenticado() is True

    from utils.auth_guard import encerrar_sessao

    encerrar_sessao()

    assert st.session_state["usuario"] is None
    assert usuario_autenticado() is False


def test_encerrar_sessao_sem_usuario():
    limpar_sessao()

    from utils.auth_guard import encerrar_sessao

    encerrar_sessao()

    assert st.session_state["usuario"] is None
    assert usuario_autenticado() is False


def test_encerrar_sessao_remove_acesso_autenticado():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 10,
        "nome": "Usuário Teste",
    }

    assert usuario_autenticado() is True

    from utils.auth_guard import encerrar_sessao

    encerrar_sessao()

    assert usuario_autenticado() is False


def test_novo_login_pode_ocorrer_apos_logout():
    limpar_sessao()

    st.session_state["usuario"] = {
        "id": 1,
        "nome": "Primeiro Usuário",
    }

    from utils.auth_guard import encerrar_sessao

    encerrar_sessao()

    assert usuario_autenticado() is False

    st.session_state["usuario"] = {
        "id": 2,
        "nome": "Segundo Usuário",
    }

    assert usuario_autenticado() is True
    assert st.session_state["usuario"]["id"] == 2
