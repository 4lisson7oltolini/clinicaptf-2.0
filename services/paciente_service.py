"""
Camada de serviço: regras de negócio de Paciente.

Esta camada é independente da interface Streamlit.
As validações são executadas aqui para garantir que
qualquer chamada ao serviço respeite as regras do domínio.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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
    pass


class DadosPacienteInvalidosError(ValueError):
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
    - trata CPF duplicado.
    """

    # -----------------------------------------------------
    # Normalização
    # -----------------------------------------------------

    nome = (
        nome or ""
    ).strip()

    cpf = limpar_cpf(
        cpf
    )

    cep = limpar_cep(
        cep
    )

    telefone = limpar_telefone(
        telefone
    ) if telefone else None


    # -----------------------------------------------------
    # Validar nome
    # -----------------------------------------------------

    if not validar_nome(nome):

        raise DadosPacienteInvalidosError(
            "Nome completo inválido."
        )


    # -----------------------------------------------------
    # Validar CPF
    # -----------------------------------------------------

    if not validar_cpf(cpf):

        raise DadosPacienteInvalidosError(
            "CPF inválido."
        )


    # -----------------------------------------------------
    # Validar CEP
    # -----------------------------------------------------

    if not validar_cep(cep):

        raise DadosPacienteInvalidosError(
            "CEP inválido."
        )


    # -----------------------------------------------------
    # Validar telefone
    # -----------------------------------------------------

    if telefone and not validar_telefone(
        telefone
    ):

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

    db.add(
        paciente
    )


    # -----------------------------------------------------
    # Salvar
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(
            paciente
        )

    except IntegrityError:

        db.rollback()

        raise PacienteJaExisteError(
            f"Já existe paciente com CPF {cpf}"
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
    Lista pacientes.

    Quando termo_busca é informado,
    pesquisa pelo nome.
    """

    query = db.query(
        Paciente
    )


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
    """

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
        True  -> paciente removido
        False -> paciente não encontrado
    """

    paciente = buscar_por_id(
        db,
        paciente_id,
    )


    if not paciente:

        return False


    db.delete(
        paciente
    )

    db.commit()

    return True
