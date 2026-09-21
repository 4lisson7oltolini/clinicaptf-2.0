from datetime import datetime

from services.auth_service import autenticar, criar_usuario
from services.consulta_service import (
    agendar_consulta,
    atualizar_status,
    buscar_consulta_por_id,
)
from services.paciente_service import criar_paciente
from services.profissional_service import criar_profissional
from services.relatorio_service import (
    listar_consultas_periodo,
    montar_linhas_consultas,
)


def test_fluxo_completo_de_atendimento_persiste_e_aparece_no_relatorio(
    db_session,
):
    usuario_criado = criar_usuario(
        db_session,
        username="admin_integracao",
        senha="senha1234",
        nome_completo="Administrador da Integração",
        perfil="admin",
    )

    usuario_autenticado = autenticar(
        db_session,
        "admin_integracao",
        "senha1234",
    )

    assert usuario_autenticado is not None
    assert usuario_autenticado.id == usuario_criado.id
    assert usuario_autenticado.perfil == "admin"

    paciente = criar_paciente(
        db_session,
        nome="Maria da Silva",
        cpf="52998224725",
        cep="01311000",
        telefone="11999999999",
    )
    profissional = criar_profissional(
        db_session,
        nome="Dr. Carlos Mendes",
        especialidade="Fisioterapia",
        registro_profissional="CREFITO-INT-001",
    )

    consulta_criada = agendar_consulta(
        db_session,
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        data_hora=datetime(2026, 10, 5, 14, 0),
        observacoes="Avaliação inicial",
    )

    db_session.expire_all()
    consulta_persistida = buscar_consulta_por_id(
        db_session,
        consulta_criada.id,
    )

    assert consulta_persistida is not None
    assert consulta_persistida.paciente_id == paciente.id
    assert consulta_persistida.profissional_id == profissional.id
    assert consulta_persistida.status == "agendada"
    assert consulta_persistida.observacoes == "Avaliação inicial"

    consulta_confirmada = atualizar_status(
        db_session,
        consulta_persistida.id,
        "confirmada",
    )
    assert consulta_confirmada.status == "confirmada"

    db_session.expire_all()
    consulta_confirmada_persistida = buscar_consulta_por_id(
        db_session,
        consulta_persistida.id,
    )
    assert consulta_confirmada_persistida.status == "confirmada"

    consulta_concluida = atualizar_status(
        db_session,
        consulta_confirmada_persistida.id,
        "concluida",
    )
    assert consulta_concluida.status == "concluida"

    db_session.expire_all()
    consulta_final = buscar_consulta_por_id(
        db_session,
        consulta_persistida.id,
    )

    assert consulta_final is not None
    assert consulta_final.status == "concluida"
    assert consulta_final.paciente.nome == "Maria da Silva"
    assert consulta_final.profissional.nome == "Dr. Carlos Mendes"

    consultas_do_periodo = listar_consultas_periodo(
        db_session,
        referencia=datetime(2026, 10, 5).date(),
        periodo="Dia",
        profissional_id=profissional.id,
        paciente_id=paciente.id,
    )
    linhas_relatorio = montar_linhas_consultas(consultas_do_periodo)

    assert len(consultas_do_periodo) == 1
    assert linhas_relatorio == [[
        "05/10/2026",
        "14:00",
        "Maria da Silva",
        "Dr. Carlos Mendes",
        "Concluída",
        "Avaliação inicial",
    ]]
