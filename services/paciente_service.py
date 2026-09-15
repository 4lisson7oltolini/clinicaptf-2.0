"""
Camada de serviço: regras de negócio de Paciente.

Esta camada é independente da interface Streamlit.

Responsabilidades:
- validar dados de pacientes;
- normalizar dados;
- criar pacientes;
- listar pacientes;
- buscar pacientes;
- remover pacientes;
- tratar erros de integridade do banco.

As regras de negócio ficam centralizadas aqui para que
também sejam aplicadas quando o serviço for utilizado
fora da interface Streamlit.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.paciente import Paciente

from utils.validators import (
    limpar_cpf,
    limpar_cep,
    limpar_telefone,
    validar_cpf,
    validar_cep,
    validar_telefone,
    validar_nome,
)


# ---------------------------------------------------------
# Exceções
# ---------------------------------------------------------


class PacienteJaExisteError(Exception):
    """Paciente já cadastrado."""

    pass


class DadosPacienteInvalidosError(ValueError):
    """Dados fornecidos para o paciente são inválidos."""

    pass


# ---------------------------------------------------------
# Criar paciente
# ---------------------------------------------------------


def criar_paciente(
    db: Session,
    nome: str,
    cpf: str,
    cep: str,
    telefone: str | None = None,
) -> Paciente:
    """
    Cria um novo paciente.

    Antes de salvar no banco:

    - normaliza CPF, CEP e telefone;
    - valida o nome;
    - valida CPF;
    - valida CEP;
    - valida telefone;
    - trata CPF duplicado;
    - executa rollback quando necessário.

    Raises:
        DadosPacienteInvalidosError:
            Quando algum dado fornecido é inválido.

        PacienteJaExisteError:
            Quando já existe um paciente com o CPF informado.
    """

    # -----------------------------------------------------
    # Normalização
    # -----------------------------------------------------

    nome = (nome or "").strip()

    cpf = limpar_cpf(cpf)

    cep = limpar_cep(cep)

    telefone = (
        limpar_telefone(telefone)
        if telefone
        else None
    )


    # -----------------------------------------------------
    # Validação do nome
    # -----------------------------------------------------

    if not validar_nome(nome):

        raise DadosPacienteInvalidosError(
            "Nome completo inválido."
        )


    # -----------------------------------------------------
    # Validação do CPF
    # -----------------------------------------------------

    if not validar_cpf(cpf):

        raise DadosPacienteInvalidosError(
            "CPF inválido."
        )


    # -----------------------------------------------------
    # Validação do CEP
    # -----------------------------------------------------

    if not validar_cep(cep):

        raise DadosPacienteInvalidosError(
            "CEP inválido."
        )


    # -----------------------------------------------------
    # Validação do telefone
    # -----------------------------------------------------

    if telefone and not validar_telefone(telefone):

        raise DadosPacienteInvalidosError(
            "Telefone inválido."
        )


    # -----------------------------------------------------
    # Criar objeto
    # -----------------------------------------------------

    paciente = Paciente(
        nome=nome,
        cpf=cpf,
        cep=cep,
        telefone=telefone,
    )

    db.add(paciente)


    # -----------------------------------------------------
    # Persistência
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(paciente)

    except IntegrityError:

        db.rollback()

        raise PacienteJaExisteError(
            f"Já existe paciente com CPF {cpf}."
        )


    return paciente


# ---------------------------------------------------------
# Listar pacientes
# ---------------------------------------------------------


def listar_pacientes(
    db: Session,
    termo_busca: str | None = None,
) -> list[Paciente]:
    """
    Lista pacientes ordenados pelo nome.

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

    query = db.query(Paciente)


    if termo_busca:

        query = query.filter(
            Paciente.nome.ilike(
                f"%{termo_busca}%"
            )
        )


    return (
        query
        .order_by(
            Paciente.nome
        )
        .all()
    )


# ---------------------------------------------------------
# Buscar paciente por ID
# ---------------------------------------------------------


def buscar_por_id(
    db: Session,
    paciente_id: int,
) -> Paciente | None:
    """
    Busca um paciente pelo ID.

    IDs inválidos retornam None em vez de executar
    uma consulta desnecessária ao banco.
    """

    if not isinstance(paciente_id, int):

        return None

    if paciente_id <= 0:

        return None


    return (
        db.query(Paciente)
        .filter(
            Paciente.id == paciente_id
        )
        .first()
    )


# ---------------------------------------------------------
# Remover paciente
# ---------------------------------------------------------


def remover_paciente(
    db: Session,
    paciente_id: int,
) -> bool:
    """
    Remove um paciente pelo ID.

    Retorna:
        True:
            paciente removido.

        False:
            paciente não encontrado ou ID inválido.

    O rollback é executado quando ocorre uma falha
    de integridade durante a exclusão.
    """

    paciente = buscar_por_id(
        db,
        paciente_id,
    )


    if not paciente:

        return False


    db.delete(paciente)


    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        return False


    return True
