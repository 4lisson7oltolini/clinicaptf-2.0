from datetime import datetime, timedelta, date, time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from models.consulta import Consulta
from models.paciente import Paciente
from models.profissional import Profissional


# ---------------------------------------------------------
# Configurações
# ---------------------------------------------------------

DURACAO_PADRAO_MINUTOS = 50

STATUS_VALIDOS = {
    "agendada",
    "confirmada",
    "concluida",
    "cancelada",
}


# ---------------------------------------------------------
# Exceções
# ---------------------------------------------------------

class ConflitoDeHorarioError(Exception):
    """Profissional já possui consulta no horário informado."""
    pass


class StatusConsultaInvalidoError(Exception):
    """Status informado não é válido."""
    pass


class DadosConsultaInvalidosError(ValueError):
    """Dados informados para a consulta são inválidos."""
    pass


# ---------------------------------------------------------
# Validação de IDs
# ---------------------------------------------------------

def _validar_id(valor: int, nome: str) -> None:
    """
    Valida um ID antes de utilizá-lo em operações do domínio.
    """

    if not isinstance(valor, int) or isinstance(valor, bool):
        raise DadosConsultaInvalidosError(
            f"{nome} deve ser um número inteiro."
        )

    if valor <= 0:
        raise DadosConsultaInvalidosError(
            f"{nome} deve ser maior que zero."
        )


# ---------------------------------------------------------
# Verificar disponibilidade do profissional
# ---------------------------------------------------------

def _profissional_ocupado(
    db: Session,
    profissional_id: int,
    data_hora: datetime,
    ignorar_id: int | None = None,
) -> bool:
    """
    Verifica se o profissional possui outra consulta
    dentro do intervalo considerado como ocupado.
    """

    inicio = data_hora - timedelta(
        minutes=DURACAO_PADRAO_MINUTOS
    )

    fim = data_hora + timedelta(
        minutes=DURACAO_PADRAO_MINUTOS
    )

    query = db.query(Consulta).filter(
        Consulta.profissional_id == profissional_id,
        Consulta.status != "cancelada",
        Consulta.data_hora > inicio,
        Consulta.data_hora < fim,
    )

    if ignorar_id is not None:
        query = query.filter(
            Consulta.id != ignorar_id
        )

    return db.query(
        query.exists()
    ).scalar()


# ---------------------------------------------------------
# Agendar consulta
# ---------------------------------------------------------

def agendar_consulta(
    db: Session,
    paciente_id: int,
    profissional_id: int,
    data_hora: datetime,
    observacoes: str | None = None,
) -> Consulta:
    """
    Cria uma nova consulta.

    Antes de salvar:
    - valida os IDs;
    - verifica se o paciente existe;
    - verifica se o profissional existe;
    - verifica conflito de horário;
    - trata erros de integridade do banco.
    """

    _validar_id(
        paciente_id,
        "ID do paciente",
    )

    _validar_id(
        profissional_id,
        "ID do profissional",
    )

    if not isinstance(data_hora, datetime):
        raise DadosConsultaInvalidosError(
            "A data e hora da consulta são inválidas."
        )

    paciente = (
        db.query(Paciente)
        .filter(
            Paciente.id == paciente_id
        )
        .first()
    )

    if paciente is None:
        raise DadosConsultaInvalidosError(
            "Paciente não encontrado."
        )

    profissional = (
        db.query(Profissional)
        .filter(
            Profissional.id == profissional_id
        )
        .first()
    )

    if profissional is None:
        raise DadosConsultaInvalidosError(
            "Profissional não encontrado."
        )

    if _profissional_ocupado(
        db,
        profissional_id,
        data_hora,
    ):
        raise ConflitoDeHorarioError(
            "O profissional já possui uma consulta próxima desse horário."
        )

    consulta = Consulta(
        paciente_id=paciente_id,
        profissional_id=profissional_id,
        data_hora=data_hora,
        observacoes=observacoes,
        status="agendada",
    )

    db.add(consulta)

    try:
        db.commit()
        db.refresh(consulta)

    except IntegrityError:
        db.rollback()

        raise DadosConsultaInvalidosError(
            "Não foi possível criar a consulta."
        )

    return consulta


# ---------------------------------------------------------
# Listar consultas
# ---------------------------------------------------------

def listar_consultas(
    db: Session,
    profissional_id: int | None = None,
    dia: date | None = None,
    incluir_canceladas: bool = True,
) -> list[Consulta]:

    query = (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
    )

    if profissional_id is not None:

        query = query.filter(
            Consulta.profissional_id == profissional_id
        )

    if dia is not None:

        inicio = datetime.combine(
            dia,
            time.min,
        )

        fim = datetime.combine(
            dia,
            time.max,
        )

        query = query.filter(
            Consulta.data_hora >= inicio,
            Consulta.data_hora <= fim,
        )

    if not incluir_canceladas:

        query = query.filter(
            Consulta.status != "cancelada"
        )

    return (
        query
        .order_by(
            Consulta.data_hora
        )
        .all()
    )


# ---------------------------------------------------------
# Histórico do paciente
# ---------------------------------------------------------

def listar_consultas_do_paciente(
    db: Session,
    paciente_id: int,
    incluir_canceladas: bool = True,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    profissional_id: int | None = None,
    status: str | None = None,
) -> list[Consulta]:

    query = (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
        .filter(
            Consulta.paciente_id == paciente_id
        )
    )

    if data_inicio is not None:

        inicio = datetime.combine(
            data_inicio,
            time.min,
        )

        query = query.filter(
            Consulta.data_hora >= inicio
        )

    if data_fim is not None:

        fim = datetime.combine(
            data_fim,
            time.max,
        )

        query = query.filter(
            Consulta.data_hora <= fim
        )

    if profissional_id is not None:

        query = query.filter(
            Consulta.profissional_id == profissional_id
        )

    if status is not None:

        if status not in STATUS_VALIDOS:

            raise StatusConsultaInvalidoError(
                f"Status inválido: {status}"
            )

        query = query.filter(
            Consulta.status == status
        )

    if not incluir_canceladas:

        query = query.filter(
            Consulta.status != "cancelada"
        )

    return (
        query
        .order_by(
            Consulta.data_hora.desc()
        )
        .all()
    )


# ---------------------------------------------------------
# Consultas do dia
# ---------------------------------------------------------

def listar_consultas_do_dia(
    db: Session,
    dia: date | None = None,
) -> list[Consulta]:

    dia = dia or date.today()

    return listar_consultas(
        db,
        dia=dia,
        incluir_canceladas=False,
    )


# ---------------------------------------------------------
# Buscar consulta por ID
# ---------------------------------------------------------

def buscar_consulta_por_id(
    db: Session,
    consulta_id: int,
) -> Consulta | None:

    if not isinstance(consulta_id, int):
        return None

    if isinstance(consulta_id, bool):
        return None

    if consulta_id <= 0:
        return None

    return (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
        .filter(
            Consulta.id == consulta_id
        )
        .first()
    )


# ---------------------------------------------------------
# Atualizar status
# ---------------------------------------------------------

def atualizar_status(
    db: Session,
    consulta_id: int,
    novo_status: str,
) -> Consulta | None:

    if novo_status not in STATUS_VALIDOS:

        raise StatusConsultaInvalidoError(
            f"Status inválido: {novo_status}"
        )

    consulta = buscar_consulta_por_id(
        db,
        consulta_id,
    )

    if not consulta:
        return None

    consulta.status = novo_status

    try:
        db.commit()
        db.refresh(consulta)

    except IntegrityError:
        db.rollback()

        raise DadosConsultaInvalidosError(
            "Não foi possível atualizar o status da consulta."
        )

    return consulta


# ---------------------------------------------------------
# Cancelar consulta
# ---------------------------------------------------------

def cancelar_consulta(
    db: Session,
    consulta_id: int,
) -> Consulta | None:

    return atualizar_status(
        db,
        consulta_id,
        "cancelada",
    )


# ---------------------------------------------------------
# Contar consultas ativas
# ---------------------------------------------------------

def contar_consultas_ativas(
    db: Session,
) -> int:

    return (
        db.query(Consulta)
        .filter(
            Consulta.status != "cancelada"
        )
        .count()
    )


# ---------------------------------------------------------
# Verificar profissional ocupado agora
# ---------------------------------------------------------

def profissional_ocupado_agora(
    db: Session,
    profissional_id: int,
) -> bool:

    if not isinstance(profissional_id, int):
        return False

    if isinstance(profissional_id, bool):
        return False

    if profissional_id <= 0:
        return False

    return _profissional_ocupado(
        db,
        profissional_id,
        datetime.now(),
    )