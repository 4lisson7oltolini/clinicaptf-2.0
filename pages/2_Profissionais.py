import streamlit as st
from database.connection import SessionLocal
from services.profissional_service import (
    criar_profissional,
    listar_profissionais,
    ProfissionalJaExisteError,
    DadosProfissionalInvalidosError,
)

from utils.auth_guard import exigir_login


# ---------------------------------------------------------
# Autenticação
# ---------------------------------------------------------

exigir_login()


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------

st.title("🩺 Profissionais")


# ---------------------------------------------------------
# Cadastro de profissional
# ---------------------------------------------------------

with st.form(
    "novo_profissional",
    clear_on_submit=True,
):

    nome = st.text_input(
        "Nome"
    )

    especialidade = st.text_input(
        "Especialidade"
    )

    registro = st.text_input(
        "Registro profissional (ex: CREFITO-12345)"
    )

    enviado = st.form_submit_button(
        "Cadastrar"
    )


# ---------------------------------------------------------
# Processamento do cadastro
# ---------------------------------------------------------

if enviado:

    db = SessionLocal()

    try:

        criar_profissional(
            db,
            nome=nome,
            especialidade=especialidade,
            registro_profissional=registro,
        )

        st.success(
            f"Profissional {nome} cadastrado."
        )

    except DadosProfissionalInvalidosError as erro:

        st.error(
            str(erro)
        )

    except ProfissionalJaExisteError as erro:

        st.error(
            str(erro)
        )

    finally:

        db.close()


# ---------------------------------------------------------
# Lista de profissionais
# ---------------------------------------------------------

st.subheader(
    "Profissionais cadastrados"
)


db = SessionLocal()

try:

    profissionais = listar_profissionais(
        db
    )

    if profissionais:

        st.dataframe(
            [
                {
                    "Nome": profissional.nome,
                    "Especialidade": profissional.especialidade,
                    "Registro": profissional.registro_profissional,
                }
                for profissional in profissionais
            ],
            use_container_width=True,
        )

    else:

        st.info(
            "Nenhum profissional cadastrado ainda."
        )

finally:

    db.close()