import streamlit as st
from database.connection import SessionLocal
from services.paciente_service import listar_pacientes
from services.profissional_service import (
    listar_profissionais,
)

from services.consulta_service import (
    listar_consultas_do_paciente,
    buscar_consulta_por_id,
    atualizar_status,
    cancelar_consulta,
)

from components.paciente_form import formulario_novo_paciente
from utils.auth_guard import exigir_login

# ---------------------------------------------------------
# Autenticação
# ---------------------------------------------------------

exigir_login()


# ---------------------------------------------------------
# Estado da página
# ---------------------------------------------------------

if "consulta_selecionada" not in st.session_state:
    st.session_state["consulta_selecionada"] = None


# ---------------------------------------------------------
# Configuração visual
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .historico-card {
        padding: 18px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        background-color: rgba(255,255,255,0.02);
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------

st.title("Pacientes")

st.caption(
    "Cadastro, informações e histórico dos pacientes"
)


# ---------------------------------------------------------
# Novo paciente
# ---------------------------------------------------------

with st.expander(
    "Cadastrar novo paciente",
    expanded=False,
):

    formulario_novo_paciente(
        SessionLocal
    )


st.divider()


# ---------------------------------------------------------
# Buscar pacientes e profissionais
# ---------------------------------------------------------

db = SessionLocal()

try:

    pacientes = listar_pacientes(db)

    profissionais = listar_profissionais(db)

finally:

    db.close()


# ---------------------------------------------------------
# Nenhum paciente
# ---------------------------------------------------------

if not pacientes:

    st.info(
        "Nenhum paciente cadastrado ainda."
    )

    st.stop()


# ---------------------------------------------------------
# Seleção do paciente
# ---------------------------------------------------------

st.subheader("Paciente")

paciente_selecionado = st.selectbox(
    "Selecione um paciente",
    pacientes,
    format_func=lambda paciente: (
        f"{paciente.nome} — CPF: {paciente.cpf}"
    ),
)

# ---------------------------------------------------------
# Identificação do paciente
# ---------------------------------------------------------

st.subheader(
    paciente_selecionado.nome
)

st.caption(
    "Ficha do paciente"
)


# ---------------------------------------------------------
# Abas
# ---------------------------------------------------------

aba_dados, aba_historico = st.tabs(
    [
        "Dados cadastrais",
        "Histórico de consultas",
    ]
)


# =========================================================
# ABA — DADOS CADASTRAIS
# =========================================================

with aba_dados:

    st.subheader(
        "Informações pessoais"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Nome",
            paciente_selecionado.nome,
        )

        st.metric(
            "CPF",
            paciente_selecionado.cpf,
        )

    with col2:

        st.metric(
            "CEP",
            paciente_selecionado.cep,
        )

        st.metric(
            "Telefone",
            paciente_selecionado.telefone
            or "Não informado",
        )


# =========================================================
# ABA — HISTÓRICO DE CONSULTAS
# =========================================================

with aba_historico:

    st.subheader(
        "Histórico de consultas"
    )


    # -----------------------------------------------------
    # Filtros
    # -----------------------------------------------------

    st.markdown(
        "**Filtros do histórico**"
    )

    col1, col2 = st.columns(2)

    with col1:

        data_inicio = st.date_input(
            "Data inicial",
            value=None,
            key="historico_data_inicio",
        )

    with col2:

        data_fim = st.date_input(
            "Data final",
            value=None,
            key="historico_data_fim",
        )


    col1, col2 = st.columns(2)


    with col1:

        profissionais_opcoes = [
            None
        ] + profissionais

        profissional_filtro = st.selectbox(
            "Profissional",
            profissionais_opcoes,
            format_func=lambda profissional: (
                "Todos os profissionais"
                if profissional is None
                else (
                    f"{profissional.nome} — "
                    f"{profissional.especialidade}"
                )
            ),
            key="historico_profissional",
        )


    with col2:

        status_opcoes = [
            None,
            "agendada",
            "confirmada",
            "concluida",
            "cancelada",
        ]

        status_nomes = {
            None: "Todos os status",
            "agendada": "Agendada",
            "confirmada": "Confirmada",
            "concluida": "Concluída",
            "cancelada": "Cancelada",
        }

        status_filtro = st.selectbox(
            "Status",
            status_opcoes,
            format_func=lambda status: (
                status_nomes[status]
            ),
            key="historico_status",
        )


    # -----------------------------------------------------
    # Validar período
    # -----------------------------------------------------

    periodo_invalido = (
        data_inicio is not None
        and data_fim is not None
        and data_inicio > data_fim
    )


    if periodo_invalido:

        st.error(
            "A data inicial não pode ser posterior "
            "à data final."
        )

        consultas = []

    else:

        # -------------------------------------------------
        # Carregar histórico filtrado
        # -------------------------------------------------

        db = SessionLocal()

        try:

            consultas = listar_consultas_do_paciente(
                db,
                paciente_id=paciente_selecionado.id,
                incluir_canceladas=True,
                data_inicio=data_inicio,
                data_fim=data_fim,
                profissional_id=(
                    profissional_filtro.id
                    if profissional_filtro is not None
                    else None
                ),
                status=status_filtro,
            )

        finally:

            db.close()


    st.divider()


    # -----------------------------------------------------
    # Resumo das consultas filtradas
    # -----------------------------------------------------

    total_consultas = len(
        consultas
    )

    consultas_concluidas = sum(
        1
        for consulta in consultas
        if consulta.status == "concluida"
    )

    consultas_agendadas = sum(
        1
        for consulta in consultas
        if consulta.status in {
            "agendada",
            "confirmada",
        }
    )

    consultas_canceladas = sum(
        1
        for consulta in consultas
        if consulta.status == "cancelada"
    )


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total",
        total_consultas,
    )

    col2.metric(
        "Concluídas",
        consultas_concluidas,
    )

    col3.metric(
        "Agendadas",
        consultas_agendadas,
    )

    col4.metric(
        "Canceladas",
        consultas_canceladas,
    )


    st.divider()


    # =====================================================
    # DETALHES DA CONSULTA
    # =====================================================

    if st.session_state["consulta_selecionada"] is not None:

        consulta_id = st.session_state[
            "consulta_selecionada"
        ]


        db = SessionLocal()

        try:

            consulta_detalhe = buscar_consulta_por_id(
                db,
                consulta_id,
            )

        finally:

            db.close()


        if consulta_detalhe is None:

            st.error(
                "A consulta selecionada não foi encontrada."
            )

            st.session_state[
                "consulta_selecionada"
            ] = None

            st.rerun()


        else:

            st.subheader(
                "Detalhes da consulta"
            )

            st.caption(
                f"Consulta #{consulta_detalhe.id}"
            )


            # -------------------------------------------------
            # Botão voltar
            # -------------------------------------------------

            if st.button(
                "Voltar para o histórico",
                use_container_width=True,
            ):

                st.session_state[
                    "consulta_selecionada"
                ] = None

                st.rerun()


            st.divider()


            # -------------------------------------------------
            # Informações principais
            # -------------------------------------------------

            col1, col2 = st.columns(2)


            with col1:

                st.markdown(
                    "**Paciente**"
                )

                st.write(
                    consulta_detalhe.paciente.nome
                )

                st.caption(
                    f"CPF: "
                    f"{consulta_detalhe.paciente.cpf}"
                )


            with col2:

                st.markdown(
                    "**Profissional**"
                )

                st.write(
                    consulta_detalhe.profissional.nome
                )

                st.caption(
                    consulta_detalhe.profissional.especialidade
                )


            st.divider()


            # -------------------------------------------------
            # Data, horário e status
            # -------------------------------------------------

            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Data",
                    consulta_detalhe.data_hora.strftime(
                        "%d/%m/%Y"
                    ),
                )


            with col2:

                st.metric(
                    "Horário",
                    consulta_detalhe.data_hora.strftime(
                        "%H:%M"
                    ),
                )


            with col3:

                status_atual = {
                    "agendada": "Agendada",
                    "confirmada": "Confirmada",
                    "concluida": "Concluída",
                    "cancelada": "Cancelada",
                }.get(
                    consulta_detalhe.status,
                    consulta_detalhe.status,
                )

                st.metric(
                    "Status",
                    status_atual,
                )


            st.divider()


            # -------------------------------------------------
            # Observações
            # -------------------------------------------------

            st.subheader(
                "Observações"
            )


            if consulta_detalhe.observacoes:

                st.info(
                    consulta_detalhe.observacoes
                )

            else:

                st.caption(
                    "Nenhuma observação registrada."
                )


            st.divider()


            # -------------------------------------------------
            # Gerenciar consulta
            # -------------------------------------------------

            st.subheader(
                "Gerenciar consulta"
            )


            status_opcoes = {
                "agendada": "Agendada",
                "confirmada": "Confirmada",
                "concluida": "Concluída",
                "cancelada": "Cancelada",
            }


            status_selecionado = st.selectbox(
                "Status da consulta",
                options=list(
                    status_opcoes.keys()
                ),
                format_func=lambda status: (
                    status_opcoes[status]
                ),
                index=list(
                    status_opcoes.keys()
                ).index(
                    consulta_detalhe.status
                ),
                key=f"status_consulta_{consulta_detalhe.id}",
            )


            if st.button(
                "Salvar status",
                use_container_width=True,
                key=f"salvar_status_{consulta_detalhe.id}",
            ):

                db = SessionLocal()

                try:

                    atualizar_status(
                        db,
                        consulta_detalhe.id,
                        status_selecionado,
                    )

                finally:

                    db.close()


                st.success(
                    "Status atualizado com sucesso."
                )

                st.rerun()


            # -------------------------------------------------
            # Cancelar consulta
            # -------------------------------------------------

            if consulta_detalhe.status != "cancelada":

                st.divider()

                st.subheader(
                    "Cancelar consulta"
                )

                st.warning(
                    "O cancelamento altera o status da "
                    "consulta para 'Cancelada'."
                )


                if st.button(
                    "Cancelar consulta",
                    use_container_width=True,
                    key=f"cancelar_consulta_{consulta_detalhe.id}",
                ):

                    db = SessionLocal()

                    try:

                        cancelar_consulta(
                            db,
                            consulta_detalhe.id,
                        )

                    finally:

                        db.close()


                    st.success(
                        "Consulta cancelada com sucesso."
                    )

                    st.rerun()


    # =====================================================
    # LISTA DO HISTÓRICO
    # =====================================================

    else:

        # -------------------------------------------------
        # Histórico vazio
        # -------------------------------------------------

        if not consultas:

            st.info(
                "Nenhuma consulta encontrada "
                "com os filtros selecionados."
            )


        # -------------------------------------------------
        # Histórico
        # -------------------------------------------------

        else:

            for consulta in consultas:

                data = consulta.data_hora.strftime(
                    "%d/%m/%Y"
                )

                horario = consulta.data_hora.strftime(
                    "%H:%M"
                )


                # -----------------------------------------
                # Nome do status
                # -----------------------------------------

                status = {
                    "agendada": "Agendada",
                    "confirmada": "Confirmada",
                    "concluida": "Concluída",
                    "cancelada": "Cancelada",
                }.get(
                    consulta.status,
                    consulta.status,
                )


                # -----------------------------------------
                # Card da consulta
                # -----------------------------------------

                with st.container(
                    border=True
                ):

                    col1, col2, col3 = st.columns(
                        [1.2, 3, 1.5]
                    )


                    # -------------------------------------
                    # Data e horário
                    # -------------------------------------

                    with col1:

                        st.markdown(
                            f"**{data}**"
                        )

                        st.caption(
                            f"Horário: {horario}"
                        )


                    # -------------------------------------
                    # Profissional
                    # -------------------------------------

                    with col2:

                        st.markdown(
                            f"**{consulta.profissional.nome}**"
                        )

                        st.caption(
                            consulta.profissional.especialidade
                        )

                        if consulta.observacoes:

                            st.caption(
                                f"Observações: "
                                f"{consulta.observacoes}"
                            )


                    # -------------------------------------
                    # Status
                    # -------------------------------------

                    with col3:

                        st.markdown(
                            "**Status**"
                        )


                        if consulta.status == "concluida":

                            st.success(
                                status
                            )

                        elif consulta.status == "cancelada":

                            st.error(
                                status
                            )

                        elif consulta.status == "confirmada":

                            st.info(
                                status
                            )

                        else:

                            st.warning(
                                status
                            )


                        # ---------------------------------
                        # Abrir consulta
                        # ---------------------------------

                        if st.button(
                            "Abrir consulta",
                            key=f"abrir_consulta_{consulta.id}",
                            use_container_width=True,
                        ):

                            st.session_state[
                                "consulta_selecionada"
                            ] = consulta.id

                            st.rerun()
