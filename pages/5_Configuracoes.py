import streamlit as st

from database.connection import SessionLocal
from services.auth_service import (
    DadosUsuarioInvalidosError,
    UsuarioJaExisteError,
    criar_usuario,
    listar_usuarios,
    remover_usuario,
)
from services.profissional_service import (
    DadosProfissionalInvalidosError,
    ProfissionalJaExisteError,
    criar_profissional_com_usuario,
)
from utils.accessibility import NIVEIS_CONTRASTE, TEMAS
from utils.auth_guard import exigir_login
from utils.permissions import usuario_e_admin


exigir_login()


st.title("Configurações de acessibilidade")
st.caption("Personalize a aparência e a leitura do sistema.")

st.session_state.setdefault(
    "ptf_tema_edicao",
    st.session_state["ptf_tema"],
)
st.session_state.setdefault(
    "ptf_contraste_edicao",
    st.session_state["ptf_contraste"],
)


with st.form("configuracoes_acessibilidade"):
    st.subheader("Aparência")

    st.radio(
        "Tema",
        options=TEMAS,
        key="ptf_tema_edicao",
        horizontal=True,
    )

    st.radio(
        "Contraste do texto",
        options=NIVEIS_CONTRASTE,
        key="ptf_contraste_edicao",
        horizontal=True,
        help="Aumente o contraste para facilitar a leitura de títulos, textos e informações secundárias.",
    )

    st.divider()

    salvar = st.form_submit_button(
        "Salvar configurações",
        use_container_width=True,
    )


if salvar:
    st.session_state["ptf_tema"] = st.session_state["ptf_tema_edicao"]
    st.session_state["ptf_contraste"] = st.session_state["ptf_contraste_edicao"]
    st.rerun()


def restaurar_configuracoes_padrao() -> None:
    st.session_state["ptf_tema"] = "Claro"
    st.session_state["ptf_contraste"] = "Padrão"
    st.session_state["ptf_tema_edicao"] = "Claro"
    st.session_state["ptf_contraste_edicao"] = "Padrão"


st.button(
    "Restaurar configurações padrão",
    on_click=restaurar_configuracoes_padrao,
)


if usuario_e_admin():
    st.divider()
    st.subheader("Cadastro de usuários")
    st.caption("Somente administradores podem criar e remover contas.")

    with st.form("novo_usuario", clear_on_submit=True):
        nome_completo = st.text_input("Nome completo")
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        perfil = st.selectbox(
            "Tipo de usuário",
            options=("admin", "profissional", "atendente"),
            format_func=lambda valor: {
                "admin": "Administrador",
                "profissional": "Profissional",
                "atendente": "Atendente",
            }[valor],
        )

        if perfil == "profissional":
            especialidade = st.text_input("Especialidade")
            registro_profissional = st.text_input(
                "Registro profissional"
            )

        cadastrar = st.form_submit_button(
            "Cadastrar usuário",
            use_container_width=True,
        )

    if cadastrar:
        db = SessionLocal()

        try:
            if perfil == "profissional":
                criar_profissional_com_usuario(
                    db,
                    nome=nome_completo,
                    especialidade=especialidade,
                    registro_profissional=registro_profissional,
                    username=username,
                    senha=senha,
                )
            else:
                criar_usuario(
                    db,
                    username=username,
                    senha=senha,
                    nome_completo=nome_completo,
                    perfil=perfil,
                )

            st.success("Usuário cadastrado com sucesso.")

        except (
            DadosUsuarioInvalidosError,
            UsuarioJaExisteError,
            DadosProfissionalInvalidosError,
            ProfissionalJaExisteError,
        ) as erro:
            st.error(str(erro))

        finally:
            db.close()

    st.subheader("Usuários cadastrados")

    db = SessionLocal()

    try:
        usuarios = listar_usuarios(db)
    finally:
        db.close()

    usuario_atual_id = st.session_state["usuario"]["id"]

    for usuario in usuarios:
        coluna_info, coluna_acao = st.columns([4, 1])

        with coluna_info:
            st.write(
                f"**{usuario.nome_completo}** · "
                f"`{usuario.username}` · {usuario.perfil.capitalize()}"
            )

        with coluna_acao:
            if usuario.id == usuario_atual_id:
                st.caption("Sessão atual")
            elif st.button(
                "Remover",
                key=f"remover_usuario_{usuario.id}",
            ):
                db = SessionLocal()

                try:
                    remover_usuario(
                        db,
                        usuario.id,
                        usuario_atual_id=usuario_atual_id,
                    )
                    st.success("Usuário removido.")
                    st.rerun()
                except DadosUsuarioInvalidosError as erro:
                    st.error(str(erro))
                finally:
                    db.close()
