from datetime import datetime, timedelta, date, time

from sqlalchemy.orm import Session, joinedload

from models.consulta import Consulta


DURACAO_PADRAO_MINUTOS = 50


class ConflitoDeHorarioError(Exception):
    pass


def _profissional_ocupado(
    db: Session,
    profissional_id: int,
    data_hora: datetime,
    ignorar_id: int | None = None,
) -> bool:
    """Verifica se o profissional já tem consulta no mesmo intervalo de tempo."""

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

    if ignorar_id:
        query = query.filter(
            Consulta.id != ignorar_id
        )

    return db.query(query.exists()).scalar()


def agendar_consulta(
    db: Session,
    paciente_id: int,
    profissional_id: int,
    data_hora: datetime,
    observacoes: str = None,
) -> Consulta:

    if _profissional_ocupado(
        db,
        profissional_id,
        data_hora,
    ):
        raise ConflitoDeHorarioError(
            "Profissional já tem consulta marcada próxima a esse horário."
        )

    consulta = Consulta(
        paciente_id=paciente_id,
        profissional_id=profissional_id,
        data_hora=data_hora,
        observacoes=observacoes,
    )

    db.add(consulta)
    db.commit()
    db.refresh(consulta)

    return consulta


def listar_consultas(
    db: Session,
    profissional_id: int | None = None,
) -> list[Consulta]:

    query = (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
    )

    if profissional_id:
        query = query.filter(
            Consulta.profissional_id == profissional_id
        )

    return (
        query
        .order_by(Consulta.data_hora)
        .all()
    )


def listar_consultas_do_dia(
    db: Session,
    dia: date | None = None,
) -> list[Consulta]:
    """Consultas não canceladas de um dia específico."""

    dia = dia or date.today()

    inicio = datetime.combine(
        dia,
        time.min,
    )

    fim = datetime.combine(
        dia,
        time.max,
    )

    return (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
        .filter(
            Consulta.data_hora >= inicio,
            Consulta.data_hora <= fim,
            Consulta.status != "cancelada",
        )
        .order_by(Consulta.data_hora)
        .all()
    )


def contar_consultas_ativas(
    db: Session,
) -> int:
    """Total de consultas marcadas, excluindo canceladas."""

    return (
        db.query(Consulta)
        .filter(
            Consulta.status != "cancelada"
        )
        .count()
    )


def profissional_ocupado_agora(
    db: Session,
    profissional_id: int,
) -> bool:
    """Verifica se o profissional está em consulta agora."""

    return _profissional_ocupado(
        db,
        profissional_id,
        datetime.now(),
    )


def atualizar_status(
    db: Session,
    consulta_id: int,
    novo_status: str,
) -> Consulta | None:

    consulta = (
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

    if not consulta:
        return None

    consulta.status = novo_status

    db.commit()
    db.refresh(consulta)

    return consulta