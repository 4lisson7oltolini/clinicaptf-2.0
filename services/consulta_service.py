from datetime import date, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from models.consulta import Consulta, STATUS_VALIDOS
from models.paciente import Paciente
from models.profissional import Profissional


DURACAO_PADRAO_MINUTOS = 50


TRANSICOES_STATUS_PERMITIDAS = {
    "agendada": {"confirmada", "cancelada"},
    "confirmada": {"concluida", "cancelada"},
    "concluida": set(),
    "cancelada": set(),
}


class ConflitoDeHorarioError(Exception):
    """Indica que existe outra consulta no mesmo período."""

    pass


class StatusConsultaInvalidoError(ValueError):
    """Indica que o status informado não é válido."""

    pass


class DadosConsultaInvalidosError(ValueError):
    """Indica que os dados da consulta são inválidos."""

    pass


def _validar_id(valor: int, nome: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise DadosConsultaInvalidosError(
            f"{nome} deve ser um número inteiro."
        )

    if valor <= 0:
        raise DadosConsultaInvalidosError(
            f"{nome} deve ser maior que zero."
        )

    return valor


def _profissional_ocupado(
    db: Session,
    profissional_id: int,
    data_hora: datetime,
    consulta_id: int | None = None,
) -> bool:
    inicio = data_hora
    fim = data_hora + timedelta(
        minutes=DURACAO_PADRAO_MINUTOS
    )

    consultas = (
        db.query(Consulta)
        .filter(
            Consulta.profissional_id == profissional_id,
            Consulta.status != "cancelada",
        )
        .all()
    )

    for consulta in consultas:

        if (
            consulta_id is not None
            and consulta.id == consulta_id
        ):
            continue

        inicio_existente = consulta.data_hora

        fim_existente = (
            consulta.data_hora
            + timedelta(
                minutes=DURACAO_PADRAO_MINUTOS
            )
        )

        if (
            inicio < fim_existente
            and fim > inicio_existente
        ):
            return True

    return False


def agendar_consulta(
    db: Session,
    paciente_id: int,
    profissional_id: int,
    data_hora: datetime,
    status: str = "agendada",
    observacoes: str | None = None,
) -> Consulta:
    paciente_id = _validar_id(
        paciente_id,
        "paciente_id",
    )

    profissional_id = _validar_id(
        profissional_id,
        "profissional_id",
    )

    if not isinstance(data_hora, datetime):
        raise DadosConsultaInvalidosError(
            "data_hora deve ser um objeto datetime."
        )

    if status not in STATUS_VALIDOS:
        raise StatusConsultaInvalidoError(
            f"Status inválido: {status}"
        )

    paciente = (
        db.query(Paciente)
        .filter(Paciente.id == paciente_id)
        .first()
    )

    if paciente is None:
        raise DadosConsultaInvalidosError(
            f"Paciente com ID {paciente_id} não encontrado."
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
            f"Profissional com ID {profissional_id} "
            "não encontrado."
        )

    if _profissional_ocupado(
        db,
        profissional_id,
        data_hora,
    ):
        raise ConflitoDeHorarioError(
            "O profissional já possui uma consulta "
            "nesse período."
        )

    consulta = Consulta(
        paciente_id=paciente_id,
        profissional_id=profissional_id,
        data_hora=data_hora,
        status=status,
        observacoes=observacoes,
    )

    db.add(consulta)

    try:
        db.commit()
        db.refresh(consulta)

    except IntegrityError:
        db.rollback()

        raise DadosConsultaInvalidosError(
            "Não foi possível cadastrar a consulta."
        )

    return consulta


def listar_consultas(
    db: Session,
    profissional_id: int | None = None,
    data: datetime | date | None = None,
    status: str | None = None,
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

        profissional_id = _validar_id(
            profissional_id,
            "profissional_id",
        )

        query = query.filter(
            Consulta.profissional_id
            == profissional_id
        )

    if data is not None:

        if isinstance(data, datetime):

            inicio = data.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

        elif isinstance(data, date):

            inicio = datetime.combine(
                data,
                datetime.min.time(),
            )

        else:

            raise DadosConsultaInvalidosError(
                "data deve ser um objeto date ou datetime."
            )

        fim = inicio + timedelta(days=1)

        query = query.filter(
            Consulta.data_hora >= inicio,
            Consulta.data_hora < fim,
        )

    if status is not None:

        if status not in STATUS_VALIDOS:
            raise StatusConsultaInvalidoError(
                f"Status inválido: {status}"
            )

        query = query.filter(
            Consulta.status == status
        )

    elif not incluir_canceladas:

        query = query.filter(
            Consulta.status != "cancelada"
        )

    return query.order_by(
        Consulta.data_hora
    ).all()


def listar_consultas_do_paciente(
    db: Session,
    paciente_id: int,
    status: str | None = None,
    data_inicio: datetime | date | None = None,
    data_fim: datetime | date | None = None,
) -> list[Consulta]:
    paciente_id = _validar_id(
        paciente_id,
        "paciente_id",
    )

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

    if status is not None:

        if status not in STATUS_VALIDOS:
            raise StatusConsultaInvalidoError(
                f"Status inválido: {status}"
            )

        query = query.filter(
            Consulta.status == status
        )

    if data_inicio is not None:

        if isinstance(data_inicio, datetime):

            inicio = data_inicio

        elif isinstance(data_inicio, date):

            inicio = datetime.combine(
                data_inicio,
                datetime.min.time(),
            )

        else:

            raise DadosConsultaInvalidosError(
                "data_inicio deve ser um objeto "
                "date ou datetime."
            )

        query = query.filter(
            Consulta.data_hora >= inicio
        )

    if data_fim is not None:

        if isinstance(data_fim, datetime):

            fim = data_fim

        elif isinstance(data_fim, date):

            fim = datetime.combine(
                data_fim,
                datetime.max.time(),
            )

        else:

            raise DadosConsultaInvalidosError(
                "data_fim deve ser um objeto "
                "date ou datetime."
            )

        query = query.filter(
            Consulta.data_hora <= fim
        )

    return query.order_by(
        Consulta.data_hora.desc()
    ).all()


def listar_consultas_do_dia(
    db: Session,
    dia: date | datetime,
) -> list[Consulta]:

    if isinstance(dia, datetime):

        inicio = dia.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    elif isinstance(dia, date):

        inicio = datetime.combine(
            dia,
            datetime.min.time(),
        )

    else:

        raise DadosConsultaInvalidosError(
            "dia deve ser um objeto date ou datetime."
        )

    fim = inicio + timedelta(days=1)

    return (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
        .filter(
            Consulta.data_hora >= inicio,
            Consulta.data_hora < fim,
        )
        .order_by(
            Consulta.data_hora
        )
        .all()
    )


def buscar_consulta_por_id(
    db: Session,
    consulta_id: int,
) -> Consulta | None:

    if (
        isinstance(consulta_id, bool)
        or not isinstance(consulta_id, int)
        or consulta_id <= 0
    ):
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


def atualizar_status(
    db: Session,
    consulta_id: int,
    novo_status: str,
) -> Consulta | None:

    consulta_id = _validar_id(
        consulta_id,
        "consulta_id",
    )

    if novo_status not in STATUS_VALIDOS:
        raise StatusConsultaInvalidoError(
            f"Status inválido: {novo_status}"
        )

    consulta = buscar_consulta_por_id(
        db,
        consulta_id,
    )

    if consulta is None:
        return None

    status_atual = consulta.status

    status_permitidos = (
        TRANSICOES_STATUS_PERMITIDAS.get(
            status_atual,
            set(),
        )
    )

    if novo_status not in status_permitidos:
        raise ValueError(
            f"Não é permitido alterar uma consulta "
            f"de '{status_atual}' para "
            f"'{novo_status}'."
        )

    consulta.status = novo_status

    try:

        db.commit()
        db.refresh(consulta)

    except IntegrityError:

        db.rollback()
        raise

    return consulta


def cancelar_consulta(
    db: Session,
    consulta_id: int,
) -> Consulta | None:

    return atualizar_status(
        db,
        consulta_id,
        "cancelada",
    )


def contar_consultas_ativas(
    db: Session,
    profissional_id: int | None = None,
) -> int:

    query = (
        db.query(Consulta)
        .filter(
            Consulta.status != "cancelada"
        )
    )

    if profissional_id is not None:

        profissional_id = _validar_id(
            profissional_id,
            "profissional_id",
        )

        query = query.filter(
            Consulta.profissional_id
            == profissional_id
        )

    return query.count()


def profissional_ocupado_agora(
    db: Session,
    profissional_id: int,
    agora: datetime | None = None,
) -> bool:

    profissional_id = _validar_id(
        profissional_id,
        "profissional_id",
    )

    if agora is None:
        agora = datetime.now()

    if not isinstance(agora, datetime):
        raise DadosConsultaInvalidosError(
            "agora deve ser um objeto datetime."
        )

    consultas = (
        db.query(Consulta)
        .filter(
            Consulta.profissional_id
            == profissional_id,
            Consulta.status != "cancelada",
        )
        .all()
    )

    for consulta in consultas:

        inicio = consulta.data_hora

        termino = (
            inicio
            + timedelta(
                minutes=DURACAO_PADRAO_MINUTOS
            )
        )

        if inicio <= agora < termino:
            return True

    return False
