"""
Serviço de autenticação.

Responsabilidades:
- criação de usuários;
- armazenamento seguro das senhas;
- autenticação;
- validação das credenciais;
- prevenção de usuários duplicados.

As senhas nunca são armazenadas em texto puro.
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.usuario import Usuario, PERFIS_VALIDOS

from utils.validators import validar_texto_obrigatorio


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class UsuarioJaExisteError(Exception):
    """Usuário já cadastrado."""

    pass


class DadosUsuarioInvalidosError(ValueError):
    """Dados informados para o usuário são inválidos."""

    pass


def _normalizar_username(username: str) -> str:
    """
    Remove espaços desnecessários do username.
    """

    return (username or "").strip()


def criar_usuario(
    db: Session,
    username: str,
    senha: str,
    nome_completo: str,
    perfil: str = "profissional",
) -> Usuario:
    """
    Cria um usuário com senha protegida por hash bcrypt.

    A senha original nunca é armazenada no banco.
    """

    username = _normalizar_username(username)
    senha = senha or ""
    nome_completo = (nome_completo or "").strip()
    perfil = (perfil or "").strip().lower()

    if perfil not in PERFIS_VALIDOS:
        raise DadosUsuarioInvalidosError(
            f"Perfil inválido. Use um dos seguintes: {', '.join(PERFIS_VALIDOS)}"
        )

    if not validar_texto_obrigatorio(
        username,
        minimo=3,
    ):
        raise DadosUsuarioInvalidosError(
            "Usuário deve possuir pelo menos 3 caracteres."
        )

    if not validar_texto_obrigatorio(
        senha,
        minimo=8,
    ):
        raise DadosUsuarioInvalidosError(
            "A senha deve possuir pelo menos 8 caracteres."
        )

    if not validar_texto_obrigatorio(
        nome_completo,
        minimo=3,
    ):
        raise DadosUsuarioInvalidosError(
            "Nome do usuário é inválido."
        )

    usuario = Usuario(
        username=username,
        senha_hash=pwd_context.hash(senha),
        nome_completo=nome_completo,
        perfil=perfil,
    )

    db.add(usuario)

    try:
        db.commit()
        db.refresh(usuario)

    except IntegrityError:
        db.rollback()

        raise UsuarioJaExisteError(
            f"Usuário '{username}' já existe"
        )

    return usuario


def autenticar(
    db: Session,
    username: str,
    senha: str,
) -> Usuario | None:
    """
    Autentica um usuário.

    Retorna:
        Usuario quando as credenciais forem válidas.
        None quando usuário ou senha forem inválidos.
    """

    username = _normalizar_username(username)
    senha = senha or ""

    if not username or not senha:
        return None

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.username == username
        )
        .first()
    )

    if usuario is None:
        return None

    if not pwd_context.verify(
        senha,
        usuario.senha_hash,
    ):
        return None

    return usuario
