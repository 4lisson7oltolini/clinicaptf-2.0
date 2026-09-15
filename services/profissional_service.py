"""
Camada de serviço: regras de negócio de Profissional.

Esta camada é independente da interface Streamlit.
As validações são executadas aqui para garantir que
qualquer chamada ao serviço respeite as regras do domínio.
"""

import re

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.profissional import Profissional

from utils.validators import validar_texto_obrigatorio


class ProfissionalJaExisteError(Exception):
    """Exceção lançada quando o profissional já está cadastrado."""

    pass


class DadosProfissionalInvalidosError(ValueError):
    """Exceção lançada quando os dados do profissional são inválidos."""

    pass


def _validar_nome_profissional(nome: str) -> bool:
    """
    Valida o nome do profissional.

    Aceita nomes como:
        João Silva
        Dr. João
        Dr. João Silva
        Dra. Maria Souza
        Maria Souza

    Não aceita:
        vazio
        números
        caracteres especiais indevidos
        nomes com apenas espaços
    """

    nome = (nome or "").strip()

    if len(nome) < 3:
        return False

    return bool(
        re.fullmatch(
            r"(Dr\.|Dra\.)?\s*[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[\s\-][A-Za-zÀ-ÖØ-öø-ÿ]+)*",
            nome,
        )
    )


def criar_profissional(
    db: Session,
    nome: str,
    especialidade: str,
    registro_profissional: str,
) -> Profissional:
    """
    Cria um novo profissional após validar os dados.
    """

    nome = (nome or "").strip()
    especialidade = (especialidade or "").strip()
    registro_profissional = (registro_profissional or "").strip()

    if not _validar_nome_profissional(nome):
        raise DadosProfissionalInvalidosError(
            "Nome do profissional é inválido."
        )

    if not validar_texto_obrigatorio(
        especialidade,
        minimo=3,
    ):
        raise DadosProfissionalInvalidosError(
            "Especialidade inválida."
        )

    if not validar_texto_obrigatorio(
        registro_profissional,
        minimo=3,
    ):
        raise DadosProfissionalInvalidosError(
            "Registro profissional inválido."
        )

    profissional = Profissional(
        nome=nome,
        especialidade=especialidade,
        registro_profissional=registro_profissional,
    )

    db.add(profissional)

    try:
        db.commit()
        db.refresh(profissional)

    except IntegrityError:
        db.rollback()

        raise ProfissionalJaExisteError(
            "Já existe um profissional com este registro."
        )

    return profissional


def listar_profissionais(
    db: Session,
    termo_busca: str | None = None,
) -> list[Profissional]:
    """
    Lista profissionais cadastrados.

    Se termo_busca for informado, pesquisa pelo nome.
    """

    query = db.query(Profissional)

    if termo_busca:
        termo_busca = termo_busca.strip()

        query = query.filter(
            Profissional.nome.ilike(
                f"%{termo_busca}%"
            )
        )

    return query.order_by(
        Profissional.nome
    ).all()


def buscar_profissional_por_id(
    db: Session,
    profissional_id: int,
) -> Profissional | None:
    """
    Busca um profissional pelo ID.
    """

    return (
        db.query(Profissional)
        .filter(
            Profissional.id == profissional_id
        )
        .first()
    )


def remover_profissional(
    db: Session,
    profissional_id: int,
) -> bool:
    """
    Remove um profissional pelo ID.

    Retorna True quando removido.
    Retorna False quando o profissional não existe.
    """

    profissional = buscar_profissional_por_id(
        db,
        profissional_id,
    )

    if not profissional:
        return False

    db.delete(profissional)
    db.commit()

    return True
