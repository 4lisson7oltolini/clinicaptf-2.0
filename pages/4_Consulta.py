import streamlit as st

from database.connection import SessionLocal

from services.consulta_service import (
    buscar_consulta_por_id,
    atualizar_status,
    cancelar_consulta,
)

from utils.auth_guard import exigir_login


# ---------------------------------------------------------
# Autenticação
# ---------------------------------------------------------

exigir_login()


# ---------------------------------------------------------
# Recuperar ID da consulta
# ---------------------------------------------------------

consulta_id = st.session_state.get(
    "consulta_selecionada"
)


if consulta_id is None:

    st.warning(
        "Nenhuma consulta foi selecionada."
    )

    if st.button("Voltar para pacientes"):

        st.switch_page(
            "pages/1_Pacientes.py"
        )

    st.stop()


# ---------------------------------------------------------
# Buscar consulta
# ---------------------------------------------------------

db = SessionLocal()

try:

    consulta = buscar_consulta_por_id(
        db,
        consulta_id,
    )

finally:

    db.close()


# ---------------------------------------------------------
# Consulta não encontrada
# ---------------------------------------------------------

if consulta is None:

    st.error(
        "A consulta não foi encontrada."
    )

    if st.button("Voltar para pacientes"):

        st.switch_page(
            "pages/1_Pacientes.py"
        )

    st.stop()


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------

st.title("Detalhes da consulta")

st.caption(
    f"Consulta #{consulta.id}"
)


st.divider()


# ---------------------------------------------------------
# Informações principais
# ---------------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    st.subheader("Paciente")

    st.write(
        consulta.paciente.nome
    )

    st.caption(
        f"CPF: {consulta.paciente.cpf}"
    )


with col2:

    st.subheader("Profissional")

    st.write(
        consulta.profissional.nome
    )

    st.caption(
        consulta.profissional.especialidade
    )


st.divider()


# ---------------------------------------------------------
# Data e horário
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Data",
        consulta.data_hora.strftime(
            "%d/%m/%Y"
        ),
    )


with col2:

    st.metric(
        "Horário",
        consulta.data_hora.strftime(
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
        consulta.status,
        consulta.status,
    )

    st.metric(
        "Status",
        status_atual,
    )


st.divider()


# ---------------------------------------------------------
# Observações
# ---------------------------------------------------------

st.subheader("Observações")


if consulta.observacoes:

    st.info(
        consulta.observacoes
    )

else:

    st.caption(
        "Nenhuma observação registrada."
    )


st.divider()


# ---------------------------------------------------------
# Alteração de status
# ---------------------------------------------------------

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
        consulta.status
    ),
)


if st.button(
    "Salvar status",
    use_container_width=True,
):

    db = SessionLocal()

    try:

        atualizar_status(
            db,
            consulta.id,
            status_selecionado,
        )

    finally:

        db.close()


    st.success(
        "Status atualizado com sucesso."
    )

    st.rerun()


# ---------------------------------------------------------
# Cancelamento
# ---------------------------------------------------------

if consulta.status != "cancelada":

    st.divider()

    st.subheader(
        "Cancelar consulta"
    )

    st.warning(
        "O cancelamento altera o status da consulta para "
        "'Cancelada'."
    )


    if st.button(
        "Cancelar consulta",
        type="secondary",
        use_container_width=True,
    ):

        db = SessionLocal()

        try:

            cancelar_consulta(
                db,
                consulta.id,
            )

        finally:

            db.close()


        st.success(
            "Consulta cancelada com sucesso."
        )

        st.rerun()


# ---------------------------------------------------------
# Voltar
# ---------------------------------------------------------

st.divider()


if st.button(
    "Voltar para pacientes",
    use_container_width=True,
):

    st.switch_page(
        "pages/1_Pacientes.py"
    )
