from datetime import datetime, timedelta

import pytest

from services.paciente_service import criar_paciente
from services.profissional_service import criar_profissional

from services.consulta_service import (
    agendar_consulta,
    buscar_consulta_por_id,
    atualizar_status,
    cancelar_consulta,
    listar_consultas,
    listar_consultas_do_dia,
    listar_consultas_do_paciente,
    contar_consultas_ativas,
    profissional_ocupado_agora,
    ConflitoDeHorarioError,
    StatusConsultaInvalidoError,
)


# ---------------------------------------------------------
# Fixture
# ---------------------------------------------------------

@pytest.fixture()
def paciente_e_profissional(db_session):
    paciente = criar_paciente(
        db_session,
        nome="Maria Silva",
        cpf="11144477735",
        cep="01311000",
    )

    profissional = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia Ortopédica",
        registro_profissional="CREFITO-12345",
    )

    return paciente, profissional


# ---------------------------------------------------------
# Agendamento
# ---------------------------------------------------------

def test_agenda_consulta_com_sucesso(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    assert consulta.id is not None
    assert consulta.status == "agendada"
    assert consulta.paciente_id == paciente.id
    assert consulta.profissional_id == profissional.id


def test_bloqueia_conflito_de_horario(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 0),
    )

    with pytest.raises(ConflitoDeHorarioError):
        agendar_consulta(
            db_session,
            paciente.id,
            profissional.id,
            datetime(2026, 10, 1, 14, 20),
        )


def test_permite_consulta_no_limite_do_horario_anterior(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 0),
    )

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 50),
    )

    assert consulta.status == "agendada"


def test_consulta_cancelada_nao_bloqueia_horario(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 0),
    )

    cancelar_consulta(
        db_session,
        consulta.id,
    )

    nova_consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 20),
    )

    assert nova_consulta.status == "agendada"


# ---------------------------------------------------------
# Listagem
# ---------------------------------------------------------

def test_lista_apenas_consultas_do_dia_informado(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    hoje = datetime.now().replace(
        hour=10,
        minute=0,
        second=0,
        microsecond=0,
    )

    amanha = hoje + timedelta(days=1)

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        hoje,
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        amanha,
    )

    consultas_de_hoje = listar_consultas_do_dia(
        db_session,
        dia=hoje.date(),
    )

    assert len(consultas_de_hoje) == 1
    assert consultas_de_hoje[0].data_hora.date() == hoje.date()


def test_lista_consultas_por_profissional(
    db_session,
):
    paciente = criar_paciente(
        db_session,
        nome="Maria Silva",
        cpf="11144477735",
        cep="01311000",
    )

    profissional1 = criar_profissional(
        db_session,
        nome="Dr. João",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-11111",
    )

    profissional2 = criar_profissional(
        db_session,
        nome="Dra. Ana",
        especialidade="Fisioterapia Esportiva",
        registro_profissional="CREFITO-22222",
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional1.id,
        datetime(2026, 10, 1, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional2.id,
        datetime(2026, 10, 1, 11, 0),
    )

    consultas = listar_consultas(
        db_session,
        profissional_id=profissional1.id,
    )

    assert len(consultas) == 1
    assert consultas[0].profissional_id == profissional1.id


def test_nao_lista_canceladas_quando_solicitado(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    cancelar_consulta(
        db_session,
        consulta.id,
    )

    consultas = listar_consultas(
        db_session,
        incluir_canceladas=False,
    )

    assert len(consultas) == 0


# ---------------------------------------------------------
# Histórico do paciente
# ---------------------------------------------------------

def test_lista_historico_do_paciente(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 2, 9, 0),
    )

    consultas = listar_consultas_do_paciente(
        db_session,
        paciente.id,
    )

    assert len(consultas) == 2


def test_filtra_historico_por_status(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    atualizar_status(
        db_session,
        consulta.id,
        "confirmada",
    )

    consultas = listar_consultas_do_paciente(
        db_session,
        paciente.id,
        status="confirmada",
    )

    assert len(consultas) == 1
    assert consultas[0].status == "confirmada"


def test_rejeita_filtro_de_status_invalido(
    db_session,
    paciente_e_profissional,
):
    paciente, _ = paciente_e_profissional

    with pytest.raises(StatusConsultaInvalidoError):
        listar_consultas_do_paciente(
            db_session,
            paciente.id,
            status="status_inexistente",
        )


def test_filtra_historico_por_periodo(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 10, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 20, 9, 0),
    )

    consultas = listar_consultas_do_paciente(
        db_session,
        paciente.id,
        data_inicio=datetime(2026, 10, 5).date(),
        data_fim=datetime(2026, 10, 15).date(),
    )

    assert len(consultas) == 1
    assert consultas[0].data_hora.date() == datetime(
        2026,
        10,
        10,
    ).date()


# ---------------------------------------------------------
# Busca por ID
# ---------------------------------------------------------

def test_busca_consulta_por_id(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 0),
    )

    encontrada = buscar_consulta_por_id(
        db_session,
        consulta.id,
    )

    assert encontrada is not None
    assert encontrada.id == consulta.id
    assert encontrada.paciente.id == paciente.id
    assert encontrada.profissional.id == profissional.id


def test_busca_consulta_inexistente_retorna_none(
    db_session,
):
    consulta = buscar_consulta_por_id(
        db_session,
        999999,
    )

    assert consulta is None


# ---------------------------------------------------------
# Status
# ---------------------------------------------------------

def test_atualiza_status_da_consulta(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 0),
    )

    atualizada = atualizar_status(
        db_session,
        consulta.id,
        "confirmada",
    )

    assert atualizada is not None
    assert atualizada.status == "confirmada"


def test_nao_permite_status_invalido(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 0),
    )

    with pytest.raises(StatusConsultaInvalidoError):
        atualizar_status(
            db_session,
            consulta.id,
            "qualquer_status",
        )


def test_cancelar_consulta(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 14, 0),
    )

    cancelada = cancelar_consulta(
        db_session,
        consulta.id,
    )

    assert cancelada is not None
    assert cancelada.status == "cancelada"


# ---------------------------------------------------------
# Contagem
# ---------------------------------------------------------

def test_conta_apenas_consultas_nao_canceladas(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta1 = agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 9, 0),
    )

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime(2026, 10, 1, 11, 0),
    )

    assert contar_consultas_ativas(db_session) == 2

    cancelar_consulta(
        db_session,
        consulta1.id,
    )

    assert contar_consultas_ativas(db_session) == 1


# ---------------------------------------------------------
# Profissional ocupado
# ---------------------------------------------------------

def test_profissional_ocupado_agora_quando_ha_consulta_no_horario_atual(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    agendar_consulta(
        db_session,
        paciente.id,
        profissional.id,
        datetime.now(),
    )

    assert profissional_ocupado_agora(
        db_session,
        profissional.id,
    ) is True


def test_profissional_livre_agora_quando_nao_ha_consulta_proxima(
    db_session,
    paciente_e_profissional,
):
    _, profissional = paciente_e_profissional

    assert profissional_ocupado_agora(
        db_session,
        profissional.id,
    ) is False


# ---------------------------------------------------------
# Relacionamentos
# ---------------------------------------------------------

def test_consulta_possui_paciente_e_profissional(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    assert consulta.paciente.id == paciente.id
    assert consulta.profissional.id == profissional.id


# ---------------------------------------------------------
# Validação do model
# ---------------------------------------------------------

def test_modelo_nao_permite_status_invalido(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    with pytest.raises(ValueError):
        consulta.status = "qualquer_status"


# ---------------------------------------------------------
# IDs inválidos
# ---------------------------------------------------------

def test_busca_consulta_com_id_zero_retorna_none(
    db_session,
):
    resultado = buscar_consulta_por_id(
        db_session,
        0,
    )

    assert resultado is None


def test_busca_consulta_com_id_negativo_retorna_none(
    db_session,
):
    resultado = buscar_consulta_por_id(
        db_session,
        -1,
    )

    assert resultado is None


def test_busca_consulta_com_id_string_retorna_none(
    db_session,
):
    resultado = buscar_consulta_por_id(
        db_session,
        "1",
    )

    assert resultado is None


def test_atualizar_status_de_consulta_inexistente_retorna_none(
    db_session,
):
    resultado = atualizar_status(
        db_session,
        999999,
        "confirmada",
    )

    assert resultado is None


def test_cancelar_consulta_inexistente_retorna_none(
    db_session,
):
    resultado = cancelar_consulta(
        db_session,
        999999,
    )

    assert resultado is None

# ---------------------------------------------------------
# Integridade dos dados
# ---------------------------------------------------------

def test_nao_permite_id_de_paciente_zero(
    db_session,
    paciente_e_profissional,
):
    _, profissional = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=0,
            profissional_id=profissional.id,
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_id_de_paciente_negativo(
    db_session,
    paciente_e_profissional,
):
    _, profissional = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=-1,
            profissional_id=profissional.id,
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_id_de_paciente_invalido(
    db_session,
    paciente_e_profissional,
):
    _, profissional = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id="1",
            profissional_id=profissional.id,
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_id_de_profissional_zero(
    db_session,
    paciente_e_profissional,
):
    paciente, _ = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=paciente.id,
            profissional_id=0,
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_id_de_profissional_negativo(
    db_session,
    paciente_e_profissional,
):
    paciente, _ = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=paciente.id,
            profissional_id=-1,
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_id_de_profissional_invalido(
    db_session,
    paciente_e_profissional,
):
    paciente, _ = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=paciente.id,
            profissional_id="1",
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_paciente_inexistente(
    db_session,
    paciente_e_profissional,
):
    _, profissional = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=999999,
            profissional_id=profissional.id,
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_profissional_inexistente(
    db_session,
    paciente_e_profissional,
):
    paciente, _ = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=paciente.id,
            profissional_id=999999,
            data_hora=datetime(2026, 10, 1, 14, 0),
        )


def test_nao_permite_data_hora_invalida(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    with pytest.raises(ValueError):
        agendar_consulta(
            db_session,
            paciente_id=paciente.id,
            profissional_id=profissional.id,
            data_hora="2026-10-01 14:00",
        )


def test_busca_consulta_com_boolean_retorna_none(
    db_session,
):
    resultado = buscar_consulta_por_id(
        db_session,
        True,
    )

    assert resultado is None

    # ---------------------------------------------------------
# Transições de status
# ---------------------------------------------------------

def test_consulta_agendada_pode_ser_confirmada(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    resultado = atualizar_status(
        db_session,
        consulta.id,
        "confirmada",
    )

    assert resultado.status == "confirmada"


def test_consulta_agendada_pode_ser_cancelada(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    resultado = atualizar_status(
        db_session,
        consulta.id,
        "cancelada",
    )

    assert resultado.status == "cancelada"


def test_consulta_confirmada_pode_ser_concluida(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    atualizar_status(
        db_session,
        consulta.id,
        "confirmada",
    )

    resultado = atualizar_status(
        db_session,
        consulta.id,
        "concluida",
    )

    assert resultado.status == "concluida"


def test_consulta_confirmada_pode_ser_cancelada(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    atualizar_status(
        db_session,
        consulta.id,
        "confirmada",
    )

    resultado = atualizar_status(
        db_session,
        consulta.id,
        "cancelada",
    )

    assert resultado.status == "cancelada"


def test_consulta_cancelada_nao_pode_ser_confirmada(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    atualizar_status(
        db_session,
        consulta.id,
        "cancelada",
    )

    with pytest.raises(ValueError):
        atualizar_status(
            db_session,
            consulta.id,
            "confirmada",
        )


def test_consulta_cancelada_nao_pode_ser_concluida(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    atualizar_status(
        db_session,
        consulta.id,
        "cancelada",
    )

    with pytest.raises(ValueError):
        atualizar_status(
            db_session,
            consulta.id,
            "concluida",
        )


def test_consulta_concluida_nao_pode_voltar_para_agendada(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    atualizar_status(
        db_session,
        consulta.id,
        "confirmada",
    )

    atualizar_status(
        db_session,
        consulta.id,
        "concluida",
    )

    with pytest.raises(ValueError):
        atualizar_status(
            db_session,
            consulta.id,
            "agendada",
        )


def test_consulta_concluida_nao_pode_ser_cancelada(
    db_session,
    paciente_e_profissional,
):
    paciente, profissional = paciente_e_profissional

    consulta = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 1, 14, 0),
    )

    atualizar_status(
        db_session,
        consulta.id,
        "confirmada",
    )

    atualizar_status(
        db_session,
        consulta.id,
        "concluida",
    )

    with pytest.raises(ValueError):
        atualizar_status(
            db_session,
            consulta.id,
            "cancelada",
        )

# ---------------------------------------------------------
# Regressão: assinaturas usadas de verdade pelas páginas
# (essas 3 funções já foram chamadas com esses parâmetros
# pelas páginas em pages/ sem que a assinatura do service
# aceitasse — os testes abaixo existem pra nunca mais
# dessincronizar página e service silenciosamente)
# ---------------------------------------------------------

def test_listar_consultas_do_paciente_aceita_filtro_de_profissional_e_canceladas(
    db_session,
):
    paciente = criar_paciente(
        db_session, nome="Maria Silva", cpf="11144477735", cep="01311000"
    )
    profissional1 = criar_profissional(
        db_session, nome="Dr. João", especialidade="Ortopedia", registro_profissional="CREFITO-1"
    )
    profissional2 = criar_profissional(
        db_session, nome="Dra. Ana", especialidade="Neurologia", registro_profissional="CREFITO-2"
    )

    agendar_consulta(db_session, paciente.id, profissional1.id, datetime(2026, 10, 1, 9, 0))
    consulta_cancelada = agendar_consulta(
        db_session, paciente.id, profissional2.id, datetime(2026, 10, 1, 11, 0)
    )
    cancelar_consulta(db_session, consulta_cancelada.id)

    # mesma chamada que pages/1_Pacientes.py faz de verdade
    resultado = listar_consultas_do_paciente(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional1.id,
        incluir_canceladas=False,
    )

    assert len(resultado) == 1
    assert resultado[0].profissional_id == profissional1.id


def test_listar_consultas_aceita_filtro_por_dia(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 9, 0))
    agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 2, 9, 0))

    # mesma chamada que pages/3_Agenda.py faz de verdade
    resultado = listar_consultas(db_session, dia=datetime(2026, 10, 1))

    assert len(resultado) == 1


def test_listar_consultas_do_dia_sem_argumento_usa_hoje(db_session, paciente_e_profissional):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime.now())

    # mesma chamada que pages/0_Inicio.py faz de verdade
    resultado = listar_consultas_do_dia(db_session)

    assert len(resultado) == 1


# ---------------------------------------------------------
# Regressão: relacionamentos acessíveis após fechar a sessão
# (as páginas sempre fecham a sessão antes de renderizar —
# se a consulta não vier com paciente/profissional já
# carregados, dá DetachedInstanceError na tela)
# ---------------------------------------------------------

def test_buscar_consulta_por_id_permite_acessar_relacionamentos_apos_fechar_sessao(
    db_session, paciente_e_profissional
):
    paciente, profissional = paciente_e_profissional
    consulta = agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 9, 0))

    encontrada = buscar_consulta_por_id(db_session, consulta.id)
    db_session.close()

    assert encontrada.paciente.nome == paciente.nome
    assert encontrada.profissional.nome == profissional.nome


def test_listar_consultas_do_paciente_permite_relacionamentos_apos_fechar_sessao(
    db_session, paciente_e_profissional
):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 9, 0))

    resultado = listar_consultas_do_paciente(db_session, paciente_id=paciente.id)
    db_session.close()

    assert resultado[0].profissional.nome == profissional.nome


def test_listar_consultas_permite_relacionamentos_apos_fechar_sessao(
    db_session, paciente_e_profissional
):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime(2026, 10, 1, 9, 0))

    resultado = listar_consultas(db_session)
    db_session.close()

    assert resultado[0].paciente.nome == paciente.nome


def test_listar_consultas_do_dia_permite_relacionamentos_apos_fechar_sessao(
    db_session, paciente_e_profissional
):
    paciente, profissional = paciente_e_profissional
    agendar_consulta(db_session, paciente.id, profissional.id, datetime.now())

    resultado = listar_consultas_do_dia(db_session)
    db_session.close()

    assert resultado[0].paciente.nome == paciente.nome