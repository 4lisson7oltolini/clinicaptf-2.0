import streamlit as st
from database.connection import SessionLocal
from services.profissional_service import (
    criar_profissional_com_usuario,
    listar_profissionais,
    ProfissionalJaExisteError,
    DadosProfissionalInvalidosError,
)

from utils.permissions import exigir_admin
exigir_admin()

st.title("Profissionais")


st.subheader("Cadastrar profissional")


with st.form(
    "novo_profissional",
    clear_on_submit=True,
):
    nome = st.text_input(
        "Nome completo",
        placeholder="Ex: Dr. Carlos Mendes",
    )

    especialidade = st.text_input(
        "Especialidade",
        placeholder="Ex: Fisioterapia",
    )

    registro = st.text_input(
        "Registro profissional",
        placeholder="Ex: CREFITO-123456",
    )

    st.divider()

    st.markdown("**Dados de acesso**")

    username = st.text_input(
        "Usuário",
        placeholder="Ex: carlos.mendes",
    )

    senha = st.text_input(
        "Senha",
        type="password",
        placeholder="Mínimo de 8 caracteres",
    )

    enviado = st.form_submit_button(
        "Cadastrar profissional",
        use_container_width=True,
    )


if enviado:
    db = SessionLocal()

    try:
        profissional = criar_profissional_com_usuario(
            db,
            nome=nome,
            especialidade=especialidade,
            registro_profissional=registro,
            username=username,
            senha=senha,
        )

        st.success(
            f"Profissional {profissional.nome} "
            "cadastrado com sucesso."
        )

    except DadosProfissionalInvalidosError as erro:
        st.error(str(erro))

    except ProfissionalJaExisteError as erro:
        st.error(str(erro))

    finally:
        db.close()


st.divider()


st.subheader("Profissionais cadastrados")


db = SessionLocal()

try:
    profissionais = listar_profissionais(db)

    if profissionais:
        st.dataframe(
            [
                {
                    "Nome": profissional.nome,
                    "Especialidade": profissional.especialidade,
                    "Registro": profissional.registro_profissional,
                    "Usuário": (
                        profissional.usuario.username
                        if profissional.usuario
                        else "Sem usuário"
                    ),
                }
                for profissional in profissionais
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Nenhum profissional cadastrado ainda."
        )

finally:
    db.close()
