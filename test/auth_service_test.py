import pytest
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

from services.auth_service import (
    criar_usuario,
    provisionar_admin_inicial,
    autenticar,
    listar_usuarios,
    remover_usuario,
    UsuarioJaExisteError,
    DadosUsuarioInvalidosError,
)


def test_provisionar_admin_inicial_cria_apenas_o_primeiro_admin(db_session):
    usuario = provisionar_admin_inicial(
        db_session,
        username="admin-inicial",
        senha="senha-segura",
        nome_completo="Administrador Inicial",
    )

    assert usuario is not None
    assert usuario.perfil == "admin"
    assert provisionar_admin_inicial(
        db_session,
        username="outro-admin",
        senha="outra-senha",
        nome_completo="Outro Administrador",
    ) is None


def test_provisionar_admin_inicial_rejeita_username_nao_admin(db_session):
    criar_usuario(
        db_session,
        username="admin-inicial",
        senha="senha-segura",
        nome_completo="Usuário Existente",
        perfil="atendente",
    )

    with pytest.raises(DadosUsuarioInvalidosError, match="não administrativa"):
        provisionar_admin_inicial(
            db_session,
            username="admin-inicial",
            senha="outra-senha",
            nome_completo="Administrador Inicial",
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


def test_rejeita_perfil_invalido(db_session):
    with pytest.raises(DadosUsuarioInvalidosError):
        criar_usuario(
            db_session,
            username="usuario",
            senha="senha123",
            nome_completo="Usuário Teste",
            perfil="gerente",
        )


def test_lista_usuarios_em_ordem_alfabetica(db_session):
    criar_usuario(
        db_session,
        username="zeta",
        senha="senha123",
        nome_completo="Zeta",
    )
    criar_usuario(
        db_session,
        username="alfa",
        senha="senha123",
        nome_completo="Alfa",
    )

    usuarios = listar_usuarios(db_session)

    assert [usuario.nome_completo for usuario in usuarios] == [
        "Alfa",
        "Zeta",
    ]


def test_criar_usuario_converte_integrity_error(db_session):
    erro_banco = IntegrityError("insert", {}, Exception("falha"))

    with patch.object(db_session, "commit", side_effect=erro_banco):
        with pytest.raises(UsuarioJaExisteError):
            criar_usuario(
                db_session,
                username="usuario",
                senha="senha123",
                nome_completo="Usuário Teste",
            )


def test_remover_usuario_atual_nao_e_permitido(db_session):
    usuario = criar_usuario(
        db_session,
        username="admin",
        senha="senha123",
        nome_completo="Administrador",
    )

    with pytest.raises(DadosUsuarioInvalidosError):
        remover_usuario(
            db_session,
            usuario.id,
            usuario_atual_id=usuario.id,
        )


def test_remover_usuario_inexistente_retorna_false(db_session):
    assert remover_usuario(db_session, 999999) is False


def test_remover_usuario_desvincula_profissional(db_session):
    from services.profissional_service import criar_profissional_com_usuario

    profissional = criar_profissional_com_usuario(
        db_session,
        nome="Dr. Usuário",
        especialidade="Cardiologia",
        registro_profissional="CRM-99999",
        username="profissional",
        senha="senha123",
    )
    usuario_id = profissional.usuario_id

    assert remover_usuario(db_session, usuario_id) is True
    db_session.refresh(profissional)

    assert profissional.usuario_id is None