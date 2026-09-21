from types import SimpleNamespace

import utils.accessibility as accessibility


def test_inicializar_preferencias_define_valores_padrao(monkeypatch):
    estado = {}
    monkeypatch.setattr(
        accessibility,
        "st",
        SimpleNamespace(session_state=estado),
    )

    accessibility.inicializar_preferencias()

    assert estado == {
        "ptf_tema": "Claro",
        "ptf_contraste": "Padrão",
    }


def test_inicializar_preferencias_preserva_preferencias_existentes(monkeypatch):
    estado = {
        "ptf_tema": "Escuro",
        "ptf_contraste": "Máximo",
    }
    monkeypatch.setattr(
        accessibility,
        "st",
        SimpleNamespace(session_state=estado),
    )

    accessibility.inicializar_preferencias()

    assert estado["ptf_tema"] == "Escuro"
    assert estado["ptf_contraste"] == "Máximo"


def test_aplicar_estilos_acessibilidade_gera_tema_escuro(monkeypatch):
    estado = {
        "ptf_tema": "Escuro",
        "ptf_contraste": "Alto",
    }
    markdown = lambda conteudo, **kwargs: setattr(
        markdown,
        "conteudo",
        conteudo,
    )
    monkeypatch.setattr(
        accessibility,
        "st",
        SimpleNamespace(session_state=estado, markdown=markdown),
    )

    accessibility.aplicar_estilos_acessibilidade()

    assert "color-scheme: dark" in markdown.conteudo
    assert "--ptf-background: #0F172A" in markdown.conteudo
    assert "--ptf-text: #F1F5F9" in markdown.conteudo
    assert "background-color: #1E293B" in markdown.conteudo


def test_aplicar_estilos_acessibilidade_gera_tema_claro_maximo(
    monkeypatch,
):
    estado = {
        "ptf_tema": "Claro",
        "ptf_contraste": "Máximo",
    }
    markdown = lambda conteudo, **kwargs: setattr(
        markdown,
        "conteudo",
        conteudo,
    )
    monkeypatch.setattr(
        accessibility,
        "st",
        SimpleNamespace(session_state=estado, markdown=markdown),
    )

    accessibility.aplicar_estilos_acessibilidade()

    assert "color-scheme: light" in markdown.conteudo
    assert "--ptf-background: #F4F7FB" in markdown.conteudo
    assert "--ptf-text: #000000" in markdown.conteudo
    assert "--ptf-text-secondary: #172033" in markdown.conteudo
