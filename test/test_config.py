import importlib

import pytest

import config


def test_validate_config_rejeita_database_url_ausente(monkeypatch):
    monkeypatch.setattr(config, "DATABASE_URL", "")

    with pytest.raises(ValueError, match="DATABASE_URL"):
        config.validate_config()


def test_validate_config_rejeita_ambiente_desconhecido(monkeypatch):
    monkeypatch.setattr(config, "DATABASE_URL", "sqlite://")
    monkeypatch.setattr(config, "APP_ENV", "staging")

    with pytest.raises(ValueError, match="APP_ENV inválido"):
        config.validate_config()


@pytest.mark.parametrize(
    "secret_key",
    ["", "dev-secret-change-me"],
)
def test_validate_config_exige_chave_segura_em_producao(
    monkeypatch,
    secret_key,
):
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql://teste")
    monkeypatch.setattr(config, "APP_ENV", "production")
    monkeypatch.setattr(config, "SECRET_KEY", secret_key)

    with pytest.raises(ValueError, match="SECRET_KEY"):
        config.validate_config()


def test_validate_config_aceita_producao_com_chave_segura(monkeypatch):
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql://teste")
    monkeypatch.setattr(config, "APP_ENV", "production")
    monkeypatch.setattr(config, "SECRET_KEY", "chave-segura")

    config.validate_config()


def test_configura_ambiente_demo_a_partir_das_variaveis_de_ambiente(
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "demo")
    monkeypatch.setenv("DEMO_DATABASE_URL", "sqlite:///demo-teste.db")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    modulo = importlib.reload(config)

    assert modulo.APP_ENV == "demo"
    assert modulo.DATABASE_URL == "sqlite:///demo-teste.db"

    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///restaurado.db")
    importlib.reload(config)
