"""
Formulário de cadastro de pacientes.

Responsável pela interface do cadastro e pela validação
dos dados antes de enviá-los para a camada de serviço.
"""

import streamlit as st
from services.paciente_service import (
    criar_paciente,
    PacienteJaExisteError,
    DadosPacienteInvalidosError,
)
from utils.validators import (
    validar_cpf,
    limpar_cpf,
    formatar_cpf,
    validar_cep,
    limpar_cep,
    formatar_cep,
    validar_telefone,
    limpar_telefone,
    formatar_telefone,
    validar_nome,
)

# ---------------------------------------------------------
# Formulário
# ---------------------------------------------------------

def formulario_novo_paciente(
    session_factory,
):
    """
    Exibe o formulário de cadastro de pacientes.

    session_factory deve ser uma função que retorna
    uma nova sessão SQLAlchemy.
    """

    with st.form(
        "form_novo_paciente",
        clear_on_submit=True,
    ):

        # -------------------------------------------------
        # Dados pessoais
        # -------------------------------------------------

        st.subheader(
            "Dados do paciente"
        )

        nome = st.text_input(
            "Nome completo",
            placeholder="Ex.: Maria da Silva",
        )

        cpf = st.text_input(
            "CPF",
            placeholder="Ex.: 529.982.247-25",
        )

        # -------------------------------------------------
        # Dados de contato
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            cep = st.text_input(
                "CEP",
                placeholder="Ex.: 88330-000",
            )

        with col2:

            telefone = st.text_input(
                "Telefone",
                placeholder="Ex.: (47) 99999-0000",
            )


        # -------------------------------------------------
        # Enviar formulário
        # -------------------------------------------------

        enviado = st.form_submit_button(
            "Cadastrar paciente",
            use_container_width=True,
        )


    # -----------------------------------------------------
    # Processamento
    # -----------------------------------------------------

    if not enviado:
        return


    # -----------------------------------------------------
    # Normalização
    # -----------------------------------------------------

    nome = nome.strip()

    cpf_limpo = limpar_cpf(
        cpf
    )

    cep_limpo = limpar_cep(
        cep
    )

    telefone_limpo = limpar_telefone(
        telefone
    )


    # -----------------------------------------------------
    # Validação do nome
    # -----------------------------------------------------

    if not validar_nome(nome):

        st.error(
            "Informe o nome completo do paciente."
        )

        return


    # -----------------------------------------------------
    # Validação do CPF
    # -----------------------------------------------------

    if not validar_cpf(cpf_limpo):

        st.error(
            "CPF inválido. "
            "Verifique os números informados."
        )

        return


    # -----------------------------------------------------
    # Validação do CEP
    # -----------------------------------------------------

    if not validar_cep(cep_limpo):

        st.error(
            "CEP inválido. "
            "Informe um CEP com 8 dígitos."
        )

        return


    # -----------------------------------------------------
    # Validação do telefone
    # -----------------------------------------------------

    if telefone_limpo and not validar_telefone(
        telefone_limpo
    ):

        st.error(
            "Telefone inválido. "
            "Informe um telefone com DDD."
        )

        return


    # -----------------------------------------------------
    # Criar paciente
    # -----------------------------------------------------

    db = session_factory()

    try:

        paciente = criar_paciente(
            db,
            nome=nome,
            cpf=cpf_limpo,
            cep=cep_limpo,
            telefone=(
                telefone_limpo
                if telefone_limpo
                else None
            ),
        )
        
    except DadosPacienteInvalidosError as erro:

        st.error(
            str(erro)
        )

        return
    
    except PacienteJaExisteError:

        st.error(
            "Já existe um paciente cadastrado "
            "com este CPF."
        )

        return

    except Exception as erro:

        st.error(
            "Não foi possível cadastrar o paciente."
        )

        st.exception(erro)

        return

    finally:

        db.close()


    # -----------------------------------------------------
    # Sucesso
    # -----------------------------------------------------

    st.success(
        f"Paciente {paciente.nome} cadastrado com sucesso."
    )

    st.info(
        f"CPF: {formatar_cpf(paciente.cpf)}\n\n"
        f"CEP: {formatar_cep(paciente.cep)}\n\n"
        f"Telefone: "
        f"{formatar_telefone(paciente.telefone)}"
        if paciente.telefone
        else (
            f"CPF: {formatar_cpf(paciente.cpf)}\n\n"
            f"CEP: {formatar_cep(paciente.cep)}"
        )
    )
