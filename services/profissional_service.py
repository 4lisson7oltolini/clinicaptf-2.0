"""
Camada de serviço: regras de negócio de Profissional.

Esta camada é independente da interface Streamlit.

Responsabilidades:
- validar dados de profissionais;
- normalizar dados;
- criar profissionais;
- criar profissionais com usuário de acesso;
- listar profissionais;
- buscar profissionais;
- remover profissionais;
- tratar erros de integridade do banco.

As regras de negócio ficam centralizadas nesta camada.
"""

import re

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.profissional import Profissional
from models.usuario import Usuario

from utils.validators import validar_texto_obrigatorio


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class ProfissionalJaExisteError(Exception):
    """Profissional já cadastrado."""

    pass


class DadosProfissionalInvalidosError(ValueError):
    """Dados fornecidos para o profissional são inválidos."""

    pass


def _validar_nome_profissional(nome: str) -> bool:
    """
    Valida o nome do profissional.

    Aceita:
        João Silva
        Dr. João
        Dr. João Silva
        Dra. Maria Souza
        Maria Souza

    Não aceita:
        vazio;
        números;
        caracteres especiais indevidos;
        nomes com apenas espaços.
    """

    nome = (nome or "").strip()

    if len(nome) < 3:
        return False

    return bool(
        re.fullmatch(
            r"(Dr\.|Dra\.)?\s*[A-Za-zÀ-ÖØ-öø-ÿ]+"
            r"(?:[\s\-][A-Za-zÀ-ÖØ-öø-ÿ]+)*",
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

    Raises:
        DadosProfissionalInvalidosError:
            Quando algum dado é inválido.

        ProfissionalJaExisteError:
            Quando o registro profissional já existe.
    """

    nome = (nome or "").strip()

    especialidade = (
        especialidade or ""
    ).strip()

    registro_profissional = (
        registro_profissional or ""
    ).strip()

    # -----------------------------------------------------
    # Validação do nome
    # -----------------------------------------------------

    if not _validar_nome_profissional(nome):

        raise DadosProfissionalInvalidosError(
            "Nome do profissional é inválido."
        )

    # -----------------------------------------------------
    # Validação da especialidade
    # -----------------------------------------------------

    if not validar_texto_obrigatorio(
        especialidade,
        minimo=3,
    ):

        raise DadosProfissionalInvalidosError(
            "Especialidade inválida."
        )

    # -----------------------------------------------------
    # Validação do registro
    # -----------------------------------------------------

    if not validar_texto_obrigatorio(
        registro_profissional,
        minimo=3,
    ):

        raise DadosProfissionalInvalidosError(
            "Registro profissional inválido."
        )

    # -----------------------------------------------------
    # Criar objeto
    # -----------------------------------------------------

    profissional = Profissional(
        nome=nome,
        especialidade=especialidade,
        registro_profissional=registro_profissional,
    )

    db.add(profissional)

    # -----------------------------------------------------
    # Persistência
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(profissional)

    except IntegrityError:

        db.rollback()

        raise ProfissionalJaExisteError(
            "Já existe um profissional com este registro."
        )

    return profissional


def criar_profissional_com_usuario(
    db: Session,
    nome: str,
    especialidade: str,
    registro_profissional: str,
    username: str,
    senha: str,
) -> Profissional:
    """
    Cria um profissional e sua conta de acesso.

    Os dois registros são criados dentro da mesma transação.

    Se ocorrer qualquer erro durante a operação,
    todas as alterações são desfeitas.

    O usuário criado recebe automaticamente
    o perfil "profissional".
    """

    nome = (nome or "").strip()

    especialidade = (
        especialidade or ""
    ).strip()

    registro_profissional = (
        registro_profissional or ""
    ).strip()

    username = (
        username or ""
    ).strip()

    senha = senha or ""

    # -----------------------------------------------------
    # Validação do nome
    # -----------------------------------------------------

    if not _validar_nome_profissional(nome):

        raise DadosProfissionalInvalidosError(
            "Nome do profissional é inválido."
        )

    # -----------------------------------------------------
    # Validação da especialidade
    # -----------------------------------------------------

    if not validar_texto_obrigatorio(
        especialidade,
        minimo=3,
    ):

        raise DadosProfissionalInvalidosError(
            "Especialidade inválida."
        )

    # -----------------------------------------------------
    # Validação do registro
    # -----------------------------------------------------

    if not validar_texto_obrigatorio(
        registro_profissional,
        minimo=3,
    ):

        raise DadosProfissionalInvalidosError(
            "Registro profissional inválido."
        )

    # -----------------------------------------------------
    # Validação do usuário
    # -----------------------------------------------------

    if not validar_texto_obrigatorio(
        username,
        minimo=3,
    ):

        raise DadosProfissionalInvalidosError(
            "Usuário deve possuir pelo menos 3 caracteres."
        )

    # -----------------------------------------------------
    # Validação da senha
    # -----------------------------------------------------

    if not validar_texto_obrigatorio(
        senha,
        minimo=8,
    ):

        raise DadosProfissionalInvalidosError(
            "A senha deve possuir pelo menos 8 caracteres."
        )

    # -----------------------------------------------------
    # Verificar profissional existente
    # -----------------------------------------------------

    profissional_existente = (
        db.query(Profissional)
        .filter(
            Profissional.registro_profissional
            == registro_profissional
        )
        .first()
    )

    if profissional_existente:

        raise ProfissionalJaExisteError(
            "Já existe um profissional com este registro."
        )

    # -----------------------------------------------------
    # Verificar usuário existente
    # -----------------------------------------------------

    usuario_existente = (
        db.query(Usuario)
        .filter(
            Usuario.username
            == username
        )
        .first()
    )

    if usuario_existente:

        raise DadosProfissionalInvalidosError(
            f"O usuário '{username}' já está em uso."
        )

    # -----------------------------------------------------
    # Criar usuário
    # -----------------------------------------------------

    usuario = Usuario(
        username=username,
        senha_hash=pwd_context.hash(senha),
        nome_completo=nome,
        perfil="profissional",
    )

    db.add(usuario)

    # -----------------------------------------------------
    # Obter ID do usuário sem realizar commit
    # -----------------------------------------------------

    db.flush()

    # -----------------------------------------------------
    # Criar profissional
    # -----------------------------------------------------

    profissional = Profissional(
        nome=nome,
        especialidade=especialidade,
        registro_profissional=registro_profissional,
        usuario_id=usuario.id,
    )

    db.add(profissional)

    # -----------------------------------------------------
    # Persistência da transação
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(profissional)

    except IntegrityError:

        db.rollback()

        raise ProfissionalJaExisteError(
            "Não foi possível criar o profissional."
        )

    except Exception:

        db.rollback()

        raise

    return profissional


def listar_profissionais(
    db: Session,
    termo_busca: str | None = None,
) -> list[Profissional]:
    """
    Lista profissionais cadastrados.

    Quando termo_busca é informado,
    pesquisa pelo nome.

    Termos vazios ou compostos apenas por espaços
    são tratados como ausência de filtro.
    """

    termo_busca = (
        termo_busca.strip()
        if termo_busca
        else None
    )

    query = db.query(Profissional)

    if termo_busca:

        query = query.filter(
            Profissional.nome.ilike(
                f"%{termo_busca}%"
            )
        )

    return (
        query
        .order_by(
            Profissional.nome
        )
        .all()
    )


def buscar_profissional_por_id(
    db: Session,
    profissional_id: int,
) -> Profissional | None:
    """
    Busca um profissional pelo ID.

    IDs inválidos retornam None.
    """

    if not isinstance(
        profissional_id,
        int,
    ):

        return None

    if profissional_id <= 0:

        return None

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

    Retorna:
        True:
            profissional removido.

        False:
            profissional inexistente ou ID inválido.

    Em caso de erro de integridade do banco,
    executa rollback e retorna False.
    """

    profissional = buscar_profissional_por_id(
        db,
        profissional_id,
    )

    if not profissional:

        return False

    db.delete(profissional)

    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        return False

    return True
