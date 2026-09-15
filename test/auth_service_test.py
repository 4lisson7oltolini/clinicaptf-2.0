import pytest

from services.auth_service import (
    criar_usuario,
    autenticar,
    UsuarioJaExisteError,
    DadosUsuarioInvalidosError,
)


def test_autentica_com_senha_correta(db_session):
    criar_usuario(
        db_session,
        username="admin",
        senha="senha123",
        nome_completo="Admin da Clínica",
    )

    usuario = autenticar(
        db_session,
        "admin",
        "senha123",
    )

    assert usuario is not None
    assert usuario.username == "admin"


def test_rejeita_senha_incorreta(db_session):
    criar_usuario(
        db_session,
        username="admin",
        senha="senha123",
        nome_completo="Admin da Clínica",
    )

    assert autenticar(
        db_session,
        "admin",
        "senha_errada",
    ) is None


def test_rejeita_usuario_inexistente(db_session):
    assert autenticar(
        db_session,
        "nao_existe",
        "qualquer",
    ) is None


def test_nao_permite_username_duplicado(db_session):
    criar_usuario(
        db_session,
        username="admin",
        senha="senha123",
        nome_completo="Admin",
    )

    with pytest.raises(UsuarioJaExisteError):
        criar_usuario(
            db_session,
            username="admin",
            senha="outrasenha",
            nome_completo="Outro Admin",
        )


def test_senha_nao_e_armazenada_em_texto_plano(db_session):
    usuario = criar_usuario(
        db_session,
        username="admin",
        senha="senha123",
        nome_completo="Admin da Clínica",
    )

    assert usuario.senha_hash != "senha123"
    assert usuario.senha_hash.startswith("$2b$")


def test_senha_hash_e_diferente_a_cada_criacao(db_session):
    usuario1 = criar_usuario(
        db_session,
        username="admin1",
        senha="senha123",
        nome_completo="Admin Um",
    )

    usuario2 = criar_usuario(
        db_session,
        username="admin2",
        senha="senha123",
        nome_completo="Admin Dois",
    )

    assert usuario1.senha_hash != usuario2.senha_hash


def test_rejeita_senha_muito_curta(db_session):
    with pytest.raises(DadosUsuarioInvalidosError):
        criar_usuario(
            db_session,
            username="admin",
            senha="1234567",
            nome_completo="Admin",
        )


def test_rejeita_username_muito_curto(db_session):
    with pytest.raises(DadosUsuarioInvalidosError):
        criar_usuario(
            db_session,
            username="ab",
            senha="senha123",
            nome_completo="Admin",
        )


def test_rejeita_nome_vazio(db_session):
    with pytest.raises(DadosUsuarioInvalidosError):
        criar_usuario(
            db_session,
            username="admin",
            senha="senha123",
            nome_completo="",
        )


def test_rejeita_credenciais_vazias(db_session):
    criar_usuario(
        db_session,
        username="admin",
        senha="senha123",
        nome_completo="Admin",
    )

    assert autenticar(
        db_session,
        "",
        "",
    ) is None


def test_username_com_espacos_e_normalizado(db_session):
    criar_usuario(
        db_session,
        username="  admin  ",
        senha="senha123",
        nome_completo="Admin",
    )

    usuario = autenticar(
        db_session,
        "admin",
        "senha123",
    )

    assert usuario is not None
    assert usuario.username == "admin"