"""
Serviço de autenticação. Usa passlib/bcrypt — nunca compare senhas com '=='.
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.usuario import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioJaExisteError(Exception):
    pass


def criar_usuario(db: Session, username: str, senha: str, nome_completo: str) -> Usuario:
    usuario = Usuario(
        username=username,
        senha_hash=pwd_context.hash(senha),
        nome_completo=nome_completo,
    )
    db.add(usuario)
    try:
        db.commit()
        db.refresh(usuario)
    except IntegrityError:
        db.rollback()
        raise UsuarioJaExisteError(f"Usuário '{username}' já existe")
    return usuario


def autenticar(db: Session, username: str, senha: str) -> Usuario | None:
    """Retorna o Usuario se as credenciais forem válidas, senão None."""
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    if usuario is None:
        return None
    if not pwd_context.verify(senha, usuario.senha_hash):
        return None
    return usuario