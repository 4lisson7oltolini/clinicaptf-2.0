import pytest

import utils.permissions as permissions


@pytest.mark.parametrize(
    ("perfil", "verificador"),
    [
        ("admin", permissions.usuario_e_admin),
        ("profissional", permissions.usuario_e_profissional),
        ("atendente", permissions.usuario_e_atendente),
    ],
)
def test_verifica_perfil_do_usuario(perfil, verificador, monkeypatch):
    monkeypatch.setattr(
        permissions,
        "obter_usuario_autenticado",
        lambda: {"perfil": perfil},
    )

    assert verificador() is True


@pytest.mark.parametrize(
    "perfil",
    ["admin", "profissional", "atendente"],
)
def test_verificador_retorna_false_para_perfil_diferente(perfil, monkeypatch):
    monkeypatch.setattr(
        permissions,
        "obter_usuario_autenticado",
        lambda: {"perfil": perfil},
    )

    assert permissions.usuario_tem_perfil("admin", "atendente") is (
        perfil in {"admin", "atendente"}
    )


def test_usuario_tem_perfil_aceita_qualquer_perfil_informado(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "obter_usuario_autenticado",
        lambda: {"perfil": "profissional"},
    )

    assert permissions.usuario_tem_perfil("admin", "profissional") is True
    assert permissions.usuario_tem_perfil("atendente") is False


def test_exigir_admin_permite_administrador(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "obter_usuario_autenticado",
        lambda: {"perfil": "admin"},
    )

    permissions.exigir_admin()


def test_exigir_admin_interrompe_perfil_nao_autorizado(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "obter_usuario_autenticado",
        lambda: {"perfil": "atendente"},
    )
    monkeypatch.setattr("streamlit.error", lambda mensagem: None)
    monkeypatch.setattr(
        "streamlit.stop",
        lambda: (_ for _ in ()).throw(RuntimeError("parou")),
    )

    with pytest.raises(RuntimeError, match="parou"):
        permissions.exigir_admin()


def test_exigir_perfil_permite_perfil_autorizado(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "obter_usuario_autenticado",
        lambda: {"perfil": "profissional"},
    )

    permissions.exigir_perfil("admin", "profissional")


def test_exigir_perfil_interrompe_perfil_nao_autorizado(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "obter_usuario_autenticado",
        lambda: {"perfil": "atendente"},
    )
    monkeypatch.setattr("streamlit.error", lambda mensagem: None)
    monkeypatch.setattr(
        "streamlit.stop",
        lambda: (_ for _ in ()).throw(RuntimeError("parou")),
    )

    with pytest.raises(RuntimeError, match="parou"):
        permissions.exigir_perfil("admin")
