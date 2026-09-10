import pytest

from services.auth_service import criar_usuario, autenticar, UsuarioJaExisteError


def test_autentica_com_senha_correta(db_session):
    criar_usuario(db_session, username="admin", senha="senha123", nome_completo="Admin da Clínica")

    usuario = autenticar(db_session, "admin", "senha123")

    assert usuario is not None
    assert usuario.username == "admin"


def test_rejeita_senha_incorreta(db_session):
    criar_usuario(db_session, username="admin", senha="senha123", nome_completo="Admin da Clínica")

    assert autenticar(db_session, "admin", "senha_errada") is None


def test_rejeita_usuario_inexistente(db_session):
    assert autenticar(db_session, "nao_existe", "qualquer") is None


def test_nao_permite_username_duplicado(db_session):
    criar_usuario(db_session, username="admin", senha="senha123", nome_completo="Admin")

    with pytest.raises(UsuarioJaExisteError):
        criar_usuario(db_session, username="admin", senha="outrasenha", nome_completo="Outro Admin")