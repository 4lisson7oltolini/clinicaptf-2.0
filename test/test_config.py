import importlib

import pytest

import config


SECRET_KEY_TESTE = "test-secret-key-32-caracteres-segura"


def recarregar_config():
    """Recarrega o módulo config após alterar as variáveis de ambiente."""
    return importlib.reload(config)


def test_configura_ambiente_e_sslmode_a_partir_dos_secrets(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://teste",
    )
    monkeypatch.setenv("DATABASE_SSLMODE", "require")
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY_TESTE)

    modulo = recarregar_config()

    assert modulo.APP_ENV == "production"
    assert modulo.DATABASE_URL == "postgresql://teste"
    assert modulo.DATABASE_SSLMODE == "require"
    assert modulo.SECRET_KEY == SECRET_KEY_TESTE


def test_producao_exige_secret_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://teste",
    )
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="SECRET_KEY não foi definida",
    ):
        recarregar_config()

    # Restaura uma configuração válida para os testes seguintes.
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY_TESTE)
    recarregar_config()


def test_producao_exige_secret_key_forte(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://teste",
    )
    monkeypatch.setenv("SECRET_KEY", "curta")

    with pytest.raises(
        ValueError,
        match="SECRET_KEY de produção deve ser forte",
    ):
        recarregar_config()

    monkeypatch.setenv("SECRET_KEY", SECRET_KEY_TESTE)
    recarregar_config()


def test_producao_exige_postgresql(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY_TESTE)

    with pytest.raises(
        ValueError,
        match="DATABASE_URL de produção deve utilizar PostgreSQL",
    ):
        recarregar_config()


def test_database_url_obrigatoria_em_producao(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY_TESTE)

    with pytest.raises(
        ValueError,
        match="DATABASE_URL não foi definida para produção",
    ):
        recarregar_config()

    # Restaura configuração válida.
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )
    monkeypatch.setenv("APP_ENV", "development")
    recarregar_config()


def test_app_env_invalido(monkeypatch):
    # DATABASE_URL precisa existir porque a validação
    # dessa variável acontece antes da validação de APP_ENV.
    monkeypatch.setenv("APP_ENV", "invalido")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )

    with pytest.raises(
        ValueError,
        match="APP_ENV inválido",
    ):
        recarregar_config()

    # Restaura configuração válida.
    monkeypatch.setenv("APP_ENV", "testing")
    recarregar_config()


def test_producao_aceita_postgresql_plus_driver(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg2://teste",
    )
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY_TESTE)

    modulo = recarregar_config()

    assert modulo.APP_ENV == "production"
    assert modulo.DATABASE_URL == "postgresql+psycopg2://teste"


def test_database_sslmode(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )
    monkeypatch.setenv("DATABASE_SSLMODE", "require")

    modulo = recarregar_config()

    assert modulo.DATABASE_SSLMODE == "require"


def test_secret_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )
    monkeypatch.setenv("SECRET_KEY", "minha-chave-de-teste")

    modulo = recarregar_config()

    assert modulo.SECRET_KEY == "minha-chave-de-teste"


def test_ambiente_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )

    modulo = recarregar_config()

    assert modulo.APP_ENV == "development"


def test_ambiente_testing(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )

    modulo = recarregar_config()

    assert modulo.APP_ENV == "testing"


def test_ambiente_demo(monkeypatch):
    monkeypatch.setenv("APP_ENV", "demo")
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./clinicaptf.db",
    )

    modulo = recarregar_config()

    assert modulo.APP_ENV == "demo"
