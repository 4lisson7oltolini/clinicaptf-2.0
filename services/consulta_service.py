from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import Session, joinedload
from models.consulta import Consulta

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
    pass


class StatusConsultaInvalidoError(Exception):
    pass


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
    """

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

    db.commit()

    db.refresh(consulta)

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
    """
    Lista consultas com filtros opcionais.
    """

    query = (
        db.query(Consulta)
        .options(
            joinedload(Consulta.paciente),
            joinedload(Consulta.profissional),
        )
    )


    # -----------------------------------------------------
    # Filtro por profissional
    # -----------------------------------------------------

    if profissional_id is not None:

        query = query.filter(
            Consulta.profissional_id == profissional_id
        )


    # -----------------------------------------------------
    # Filtro por dia
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Filtro de canceladas
    # -----------------------------------------------------

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
    """
    Lista o histórico de consultas de um paciente.

    Permite filtrar por:

    - período inicial;
    - período final;
    - profissional;
    - status;
    - consultas canceladas.
    """

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


    # -----------------------------------------------------
    # Data inicial
    # -----------------------------------------------------

    if data_inicio is not None:

        inicio = datetime.combine(
            data_inicio,
            time.min,
        )

        query = query.filter(
            Consulta.data_hora >= inicio
        )


    # -----------------------------------------------------
    # Data final
    # -----------------------------------------------------

    if data_fim is not None:

        fim = datetime.combine(
            data_fim,
            time.max,
        )

        query = query.filter(
            Consulta.data_hora <= fim
        )


    # -----------------------------------------------------
    # Profissional
    # -----------------------------------------------------

    if profissional_id is not None:

        query = query.filter(
            Consulta.profissional_id == profissional_id
        )


    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    if status is not None:

        if status not in STATUS_VALIDOS:

            raise StatusConsultaInvalidoError(
                f"Status inválido: {status}"
            )

        query = query.filter(
            Consulta.status == status
        )


    # -----------------------------------------------------
    # Canceladas
    # -----------------------------------------------------

    if not incluir_canceladas:

        query = query.filter(
            Consulta.status != "cancelada"
        )


    # -----------------------------------------------------
    # Resultado
    # -----------------------------------------------------

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
    """
    Retorna as consultas não canceladas de um determinado dia.
    """

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
    """
    Busca uma consulta pelo ID.

    Os relacionamentos paciente e profissional são
    carregados antecipadamente para evitar problemas
    com sessões encerradas.
    """

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
    """
    Atualiza o status de uma consulta.
    """

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

    db.commit()

    db.refresh(consulta)

    return consulta


# ---------------------------------------------------------
# Cancelar consulta
# ---------------------------------------------------------

def cancelar_consulta(
    db: Session,
    consulta_id: int,
) -> Consulta | None:
    """
    Cancela uma consulta.
    """

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
    """
    Conta todas as consultas que não foram canceladas.
    """

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
    """
    Verifica se o profissional está ocupado
    no horário atual.
    """

    return _profissional_ocupado(
        db,
        profissional_id,
        datetime.now(),
    )
