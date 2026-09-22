from unittest.mock import Mock

import database.initialization as initialization


def test_executar_migrations_configura_alembic_e_atualiza_ate_head(
    monkeypatch,
):
    upgrade = Mock()
    monkeypatch.setattr(initialization.command, "upgrade", upgrade)

    initialization.executar_migrations()

    upgrade.assert_called_once()
    alembic_config, revision = upgrade.call_args.args
    assert alembic_config.config_file_name.endswith("alembic.ini")
    assert revision == "head"


def test_inicializar_aplicacao_executa_migrations_fora_do_demo(monkeypatch):
    migrations = Mock()
    demo = Mock()
    monkeypatch.setattr(initialization, "executar_migrations", migrations)
    monkeypatch.setattr(initialization, "APP_ENV", "testing")
    monkeypatch.setattr(
        initialization,
        "__name__",
        initialization.__name__,
    )

    initialization.inicializar_aplicacao.cache_clear()
    initialization.inicializar_aplicacao()

    migrations.assert_called_once_with()
    demo.assert_not_called()


def test_inicializar_aplicacao_prepara_dados_no_demo(monkeypatch):
    migrations = Mock()
    demo = Mock()
    monkeypatch.setattr(initialization, "executar_migrations", migrations)
    monkeypatch.setattr(initialization, "APP_ENV", "demo")

    import seed_demo

    monkeypatch.setattr(seed_demo, "criar_dados_demo", demo)
    initialization.inicializar_aplicacao.cache_clear()
    initialization.inicializar_aplicacao()

    migrations.assert_called_once_with()
    demo.assert_called_once_with()


def test_inicializar_aplicacao_provisiona_admin_em_producao(monkeypatch):
    migrations = Mock()
    provisionar = Mock()
    monkeypatch.setattr(initialization, "executar_migrations", migrations)
    monkeypatch.setattr(
        initialization,
        "provisionar_admin_inicialmente",
        provisionar,
    )
    monkeypatch.setattr(initialization, "APP_ENV", "production")

    initialization.inicializar_aplicacao.cache_clear()
    initialization.inicializar_aplicacao()

    migrations.assert_called_once_with()
    provisionar.assert_called_once_with()
