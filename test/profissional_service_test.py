"""
Testes da camada de serviço de Profissional.
"""

import pytest
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError

from models.profissional import Profissional
from models.usuario import Usuario

from services.profissional_service import (
    DadosProfissionalInvalidosError,
    ProfissionalJaExisteError,
    buscar_profissional_por_id,
    criar_profissional,
    criar_profissional_com_usuario,
    listar_profissionais,
    remover_profissional,
)


def test_cria_profissional(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    assert profissional.id is not None
    assert profissional.nome == "Dr. Carlos Mendes"
    assert profissional.especialidade == "Cardiologia"
    assert profissional.registro_profissional == "CRM-SC-123456"


def test_cria_profissional_com_dados_normalizados(db_session):
    profissional = criar_profissional(
        db_session,
        nome="  Dr. Carlos Mendes  ",
        especialidade="  Cardiologia  ",
        registro_profissional="  CRM-SC-123456  ",
    )

    assert profissional.nome == "Dr. Carlos Mendes"
    assert profissional.especialidade == "Cardiologia"
    assert profissional.registro_profissional == "CRM-SC-123456"


@pytest.mark.parametrize(
    "nome",
    [
        "",
        "  ",
        "A",
        "123456",
        "Dr. 123",
        "@@@",
    ],
)
def test_rejeita_nome_profissional_invalido(db_session, nome):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome=nome,
            especialidade="Cardiologia",
            registro_profissional="CRM-SC-123456",
        )


@pytest.mark.parametrize(
    "nome",
    [
        "João Silva",
        "Dr. João Silva",
        "Dra. Maria Souza",
        "Maria Souza",
        "João-Silva",
    ],
)
def test_aceita_nome_profissional_valido(db_session, nome):
    profissional = criar_profissional(
        db_session,
        nome=nome,
        especialidade="Cardiologia",
        registro_profissional=f"CRM-{len(nome)}",
    )

    assert profissional.nome == nome


@pytest.mark.parametrize(
    "especialidade",
    [
        "",
        "  ",
        "A",
        None,
    ],
)
def test_rejeita_especialidade_invalida(db_session, especialidade):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="Dr. Carlos Mendes",
            especialidade=especialidade,
            registro_profissional="CRM-SC-123456",
        )


@pytest.mark.parametrize(
    "registro",
    [
        "",
        "  ",
        "A",
        None,
    ],
)
def test_rejeita_registro_profissional_invalido(db_session, registro):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional(
            db_session,
            nome="Dr. Carlos Mendes",
            especialidade="Cardiologia",
            registro_profissional=registro,
        )


def test_rejeita_registro_profissional_duplicado(db_session):
    criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    with pytest.raises(ProfissionalJaExisteError):
        criar_profissional(
            db_session,
            nome="Dr. João Silva",
            especialidade="Ortopedia",
            registro_profissional="CRM-SC-123456",
        )


def test_busca_profissional_por_id(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    encontrado = buscar_profissional_por_id(
        db_session,
        profissional.id,
    )

    assert encontrado is not None
    assert encontrado.id == profissional.id
    assert encontrado.nome == "Dr. Carlos Mendes"


@pytest.mark.parametrize(
    "profissional_id",
    [
        0,
        -1,
        None,
        "1",
        1.5,
    ],
)
def test_busca_profissional_com_id_invalido(
    db_session,
    profissional_id,
):
    resultado = buscar_profissional_por_id(
        db_session,
        profissional_id,
    )

    assert resultado is None


def test_busca_profissional_inexistente(db_session):
    resultado = buscar_profissional_por_id(
        db_session,
        9999,
    )

    assert resultado is None


def test_lista_profissionais(db_session):
    criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    criar_profissional(
        db_session,
        nome="Dra. Maria Souza",
        especialidade="Ortopedia",
        registro_profissional="CRM-SC-654321",
    )

    profissionais = listar_profissionais(db_session)

    assert len(profissionais) == 2


def test_lista_profissionais_ordenados_por_nome(db_session):
    criar_profissional(
        db_session,
        nome="Zé Carlos",
        especialidade="Cardiologia",
        registro_profissional="CRM-000001",
    )

    criar_profissional(
        db_session,
        nome="Ana Souza",
        especialidade="Ortopedia",
        registro_profissional="CRM-000002",
    )

    profissionais = listar_profissionais(db_session)

    assert profissionais[0].nome == "Ana Souza"
    assert profissionais[1].nome == "Zé Carlos"


def test_lista_profissionais_por_termo(db_session):
    criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    criar_profissional(
        db_session,
        nome="Dra. Maria Souza",
        especialidade="Ortopedia",
        registro_profissional="CRM-SC-654321",
    )

    profissionais = listar_profissionais(
        db_session,
        termo_busca="Carlos",
    )

    assert len(profissionais) == 1
    assert profissionais[0].nome == "Dr. Carlos Mendes"


def test_lista_profissionais_com_termo_vazio(db_session):
    criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    profissionais = listar_profissionais(
        db_session,
        termo_busca="   ",
    )

    assert len(profissionais) == 1


def test_remove_profissional(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )

    resultado = remover_profissional(
        db_session,
        profissional.id,
    )

    assert resultado is True

    encontrado = buscar_profissional_por_id(
        db_session,
        profissional.id,
    )

    assert encontrado is None


@pytest.mark.parametrize(
    "profissional_id",
    [
        0,
        -1,
        None,
        "1",
    ],
)
def test_remove_profissional_com_id_invalido(
    db_session,
    profissional_id,
):
    resultado = remover_profissional(
        db_session,
        profissional_id,
    )

    assert resultado is False


def test_remove_profissional_inexistente(db_session):
    resultado = remover_profissional(
        db_session,
        9999,
    )

    assert resultado is False


def test_remove_profissional_retorna_false_em_erro_de_integridade(db_session):
    profissional = criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Cardiologia",
        registro_profissional="CRM-SC-123456",
    )
    erro_banco = IntegrityError("delete", {}, Exception("falha"))

    with patch.object(db_session, "commit", side_effect=erro_banco):
        resultado = remover_profissional(db_session, profissional.id)

    assert resultado is False


def test_cria_profissional_com_usuario(db_session):
    profissional = criar_profissional_com_usuario(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-123456",
        username="carlos",
        senha="senha1234",
    )

    assert profissional.id is not None
    assert profissional.usuario_id is not None

    usuario = (
        db_session.query(Usuario)
        .filter(
            Usuario.username == "carlos"
        )
        .first()
    )

    assert usuario is not None
    assert usuario.perfil == "profissional"
    assert usuario.nome_completo == "Dr. Carlos Mendes"
    assert profissional.usuario_id == usuario.id


def test_senha_do_profissional_e_armazenada_como_hash(
    db_session,
):
    criar_profissional_com_usuario(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-123456",
        username="carlos",
        senha="senha1234",
    )

    usuario = (
        db_session.query(Usuario)
        .filter(
            Usuario.username == "carlos"
        )
        .first()
    )

    assert usuario is not None
    assert usuario.senha_hash != "senha1234"
    assert len(usuario.senha_hash) > 20


def test_profissional_fica_vinculado_ao_usuario(
    db_session,
):
    profissional = criar_profissional_com_usuario(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-123456",
        username="carlos",
        senha="senha1234",
    )

    usuario = (
        db_session.query(Usuario)
        .filter(
            Usuario.id == profissional.usuario_id
        )
        .first()
    )

    assert usuario is not None
    assert usuario.profissional is not None
    assert usuario.profissional.id == profissional.id


def test_nao_cria_profissional_com_usuario_duplicado(
    db_session,
):
    criar_profissional_com_usuario(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-123456",
        username="carlos",
        senha="senha1234",
    )

    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional_com_usuario(
            db_session,
            nome="Dr. João Silva",
            especialidade="Ortopedia",
            registro_profissional="CREFITO-999999",
            username="carlos",
            senha="outrasenha",
        )

    profissionais = db_session.query(Profissional).all()
    usuarios = db_session.query(Usuario).all()

    assert len(profissionais) == 1
    assert len(usuarios) == 1


def test_nao_cria_usuario_quando_registro_profissional_ja_existe(
    db_session,
):
    criar_profissional_com_usuario(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-123456",
        username="carlos",
        senha="senha1234",
    )

    with pytest.raises(ProfissionalJaExisteError):
        criar_profissional_com_usuario(
            db_session,
            nome="Dr. João Silva",
            especialidade="Ortopedia",
            registro_profissional="CREFITO-123456",
            username="joao",
            senha="senha1234",
        )

    profissionais = db_session.query(Profissional).all()
    usuarios = db_session.query(Usuario).all()

    assert len(profissionais) == 1
    assert len(usuarios) == 1


def test_criacao_conjunta_converte_integrity_error(db_session):
    erro_banco = IntegrityError("insert", {}, Exception("falha"))

    with patch.object(db_session, "commit", side_effect=erro_banco):
        with pytest.raises(ProfissionalJaExisteError):
            criar_profissional_com_usuario(
                db_session,
                nome="Dr. Carlos Mendes",
                especialidade="Fisioterapia",
                registro_profissional="CREFITO-123456",
                username="carlos",
                senha="senha1234",
            )


def test_criacao_conjunta_repropaga_erro_inesperado(db_session):
    erro = RuntimeError("falha inesperada")

    with patch.object(db_session, "commit", side_effect=erro):
        with pytest.raises(RuntimeError, match="falha inesperada"):
            criar_profissional_com_usuario(
                db_session,
                nome="Dr. Carlos Mendes",
                especialidade="Fisioterapia",
                registro_profissional="CREFITO-123456",
                username="carlos",
                senha="senha1234",
            )


def test_rejeita_senha_com_menos_de_8_caracteres(
    db_session,
):
    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional_com_usuario(
            db_session,
            nome="Dr. Carlos Mendes",
            especialidade="Fisioterapia",
            registro_profissional="CREFITO-123456",
            username="carlos",
            senha="1234567",
        )

    assert db_session.query(Profissional).count() == 0
    assert db_session.query(Usuario).count() == 0


def test_aceita_senha_com_exatamente_8_caracteres(
    db_session,
):
    profissional = criar_profissional_com_usuario(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-123456",
        username="carlos",
        senha="12345678",
    )

    assert profissional.id is not None
    assert profissional.usuario_id is not None

    usuario = (
        db_session.query(Usuario)
        .filter(
            Usuario.username == "carlos"
        )
        .first()
    )

    assert usuario is not None
    assert usuario.perfil == "profissional"


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("nome", ""),
        ("nome", "A"),
        ("nome", "123456"),
        ("especialidade", ""),
        ("especialidade", "A"),
        ("registro_profissional", ""),
        ("registro_profissional", "A"),
        ("username", ""),
        ("username", "ab"),
        ("senha", ""),
    ],
)
def test_rejeita_dados_invalidos_na_criacao_conjunta(
    db_session,
    campo,
    valor,
):
    dados = {
        "nome": "Dr. Carlos Mendes",
        "especialidade": "Fisioterapia",
        "registro_profissional": "CREFITO-123456",
        "username": "carlos",
        "senha": "senha1234",
    }

    dados[campo] = valor

    with pytest.raises(DadosProfissionalInvalidosError):
        criar_profissional_com_usuario(
            db_session,
            **dados,
        )

    assert db_session.query(Profissional).count() == 0
    assert db_session.query(Usuario).count() == 0
