from datetime import datetime, date, time

import streamlit as st

from database.connection import SessionLocal

from services.paciente_service import listar_pacientes
from services.profissional_service import listar_profissionais

from services.consulta_service import (
    agendar_consulta,
    listar_consultas,
    atualizar_status,
    cancelar_consulta,
    ConflitoDeHorarioError,
    StatusConsultaInvalidoError,
)

from utils.auth_guard import exigir_login, obter_usuario_autenticado


exigir_login()

usuario = obter_usuario_autenticado()
profissional_logado_id = usuario.get("profissional_id")


st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .agenda-subtitle {
        color: #9CA3AF;
        font-size: 0.95rem;
        margin-top: -12px;
        margin-bottom: 25px;
    }

    .consulta-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        background-color: rgba(255,255,255,0.025);
        margin-bottom: 12px;
    }

    .consulta-horario {
        font-size: 1.55rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .consulta-paciente {
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 3px;
    }

    .consulta-profissional {
        color: #9CA3AF;
        font-size: 0.9rem;
    }

    .status {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .status-agendada {
        background-color: rgba(59,130,246,0.15);
        color: #60A5FA;
    }

    .status-confirmada {
        background-color: rgba(34,197,94,0.15);
        color: #4ADE80;
    }

    .status-concluida {
        background-color: rgba(168,85,247,0.15);
        color: #C084FC;
    }

    .status-cancelada {
        background-color: rgba(239,68,68,0.15);
        color: #F87171;
    }

    .agenda-section {
        margin-top: 25px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


st.title("Agenda")

st.markdown(
    '<div class="agenda-subtitle">'
    "Gerenciamento de consultas da Clínica PTF 2.0"
    "</div>",
    unsafe_allow_html=True,
)


db = SessionLocal()

try:
    pacientes = listar_pacientes(db)
    profissionais = listar_profissionais(db)

finally:
    db.close()

if usuario.get("perfil") == "profissional":
    profissionais = [
        profissional
        for profissional in profissionais
        if profissional.id == profissional_logado_id
    ]

    if not profissionais:
        st.error(
            "Seu usuário profissional não está vinculado a um cadastro "
            "de profissional. Solicite ao administrador a correção do cadastro."
        )
        st.stop()


st.markdown("### Filtros da agenda")


col1, col2, col3 = st.columns([1.2, 2, 1])


with col1:

    data_filtro = st.date_input(
        "Data",
        value=date.today(),
    )


with col2:

    if usuario.get("perfil") == "profissional":
        opcoes_profissionais = profissionais
    else:
        opcoes_profissionais = [None] + profissionais

    profissional_filtro = st.selectbox(
        "Profissional",
        opcoes_profissionais,
        format_func=lambda profissional: (
            "Todos os profissionais"
            if profissional is None
            else profissional.nome
        ),
        disabled=usuario.get("perfil") == "profissional",
    )


with col3:

    incluir_canceladas = st.checkbox(
        "Mostrar canceladas",
        value=False,
    )


db = SessionLocal()

try:

    consultas = listar_consultas(
        db,
        profissional_id=(
            profissional_filtro.id
            if profissional_filtro
            else None
        ),
        data=data_filtro,
        incluir_canceladas=incluir_canceladas,
    )

finally:

    db.close()


st.markdown(
    '<div class="agenda-section">'
    "<h3>Nova consulta</h3>"
    "</div>",
    unsafe_allow_html=True,
)


if not pacientes:

    st.warning(
        "Nenhum paciente cadastrado. "
        "Cadastre um paciente antes de criar uma consulta."
    )

elif not profissionais:

    st.warning(
        "Nenhum profissional cadastrado. "
        "Cadastre um profissional antes de criar uma consulta."
    )

else:

    with st.form(
        "nova_consulta",
        clear_on_submit=True,
    ):

        with st.container(border=True):

            st.markdown("#### Dados da consulta")

            col1, col2 = st.columns(2)

            with col1:

                paciente = st.selectbox(
                    "Paciente",
                    pacientes,
                    format_func=lambda p: p.nome,
                )

            with col2:

                profissional = st.selectbox(
                    "Profissional",
                    profissionais,
                    format_func=lambda p: (
                        f"{p.nome} — {p.especialidade}"
                    ),
                )

            col1, col2 = st.columns(2)

            with col1:

                data_consulta = st.date_input(
                    "Data da consulta",
                    value=data_filtro,
                )

            with col2:

                hora_consulta = st.time_input(
                    "Horário",
                    value=time(9, 0),
                )

            observacoes = st.text_area(
                "Observações",
                placeholder=(
                    "Adicione observações sobre a consulta, "
                    "caso necessário."
                ),
            )

            enviado = st.form_submit_button(
                "Agendar consulta",
                use_container_width=True,
            )


    if enviado:

        data_hora = datetime.combine(
            data_consulta,
            hora_consulta,
        )

        db = SessionLocal()

        try:

            agendar_consulta(
                db,
                paciente_id=paciente.id,
                profissional_id=profissional.id,
                data_hora=data_hora,
                observacoes=(
                    observacoes.strip()
                    or None
                ),
            )

            st.success(
                "Consulta agendada com sucesso."
            )

            st.rerun()

        except ConflitoDeHorarioError as erro:

            st.error(
                str(erro)
            )

        except StatusConsultaInvalidoError as erro:

            st.error(
                str(erro)
            )

        finally:

            db.close()


st.markdown(
    '<div class="agenda-section">'
    "<h3>Consultas do dia</h3>"
    "</div>",
    unsafe_allow_html=True,
)


st.caption(
    data_filtro.strftime(
        "%A, %d de %B de %Y"
    ).capitalize()
)


if not consultas:

    st.info(
        "Nenhuma consulta encontrada para os filtros selecionados."
    )

else:

    for consulta in consultas:

        horario = consulta.data_hora.strftime(
            "%H:%M"
        )

        status = consulta.status

        if status == "agendada":

            status_label = "Agendada"
            status_class = "status-agendada"

        elif status == "confirmada":

            status_label = "Confirmada"
            status_class = "status-confirmada"

        elif status == "concluida":

            status_label = "Concluída"
            status_class = "status-concluida"

        else:

            status_label = "Cancelada"
            status_class = "status-cancelada"

        with st.container():

            st.markdown(
                '<div class="consulta-card">',
                unsafe_allow_html=True,
            )

            col_hora, col_info, col_status = st.columns(
                [1, 4, 1.5]
            )

            with col_hora:

                st.markdown(
                    f'<div class="consulta-horario">'
                    f"{horario}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                st.caption("50 min")

            with col_info:

                st.markdown(
                    f'<div class="consulta-paciente">'
                    f"{consulta.paciente.nome}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div class="consulta-profissional">'
                    f"{consulta.profissional.nome}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                st.caption(
                    consulta.profissional.especialidade
                )

                if consulta.observacoes:

                    st.caption(
                        f"Observações: {consulta.observacoes}"
                    )

            with col_status:

                st.markdown(
                    f'<span class="status {status_class}">'
                    f"{status_label}"
                    f"</span>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        if status != "cancelada":

            col1, col2, col3, col4 = st.columns(
                [1, 1, 1, 3]
            )

            if status == "agendada":

                with col1:

                    if st.button(
                        "Confirmar",
                        key=f"confirmar_{consulta.id}",
                        use_container_width=True,
                    ):

                        db = SessionLocal()

                        try:

                            atualizar_status(
                                db,
                                consulta.id,
                                "confirmada",
                            )

                            st.success(
                                "Consulta confirmada com sucesso."
                            )

                            st.rerun()

                        except StatusConsultaInvalidoError as erro:

                            st.error(
                                str(erro)
                            )

                        finally:

                            db.close()

            elif status == "confirmada":

                with col1:

                    if st.button(
                        "Concluir",
                        key=f"concluir_{consulta.id}",
                        use_container_width=True,
                    ):

                        db = SessionLocal()

                        try:

                            atualizar_status(
                                db,
                                consulta.id,
                                "concluida",
                            )

                            st.success(
                                "Consulta concluída com sucesso."
                            )

                            st.rerun()

                        except StatusConsultaInvalidoError as erro:

                            st.error(
                                str(erro)
                            )

                        finally:

                            db.close()

            with col2:

                if st.button(
                    "Cancelar",
                    key=f"cancelar_{consulta.id}",
                    use_container_width=True,
                ):

                    db = SessionLocal()

                    try:

                        cancelar_consulta(
                            db,
                            consulta.id,
                        )

                        st.success(
                            "Consulta cancelada com sucesso."
                        )

                        st.rerun()

                    except StatusConsultaInvalidoError as erro:

                        st.error(
                            str(erro)
                        )

                    finally:

                        db.close()