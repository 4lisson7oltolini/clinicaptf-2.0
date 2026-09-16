"""
Model de Usuário do sistema (login da clínica).

A senha NUNCA é armazenada em texto puro —
sempre como hash bcrypt.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.connection import Base


PERFIS_VALIDOS = {
    "admin",
    "profissional",
}


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String(60),
        unique=True,
        nullable=False,
        index=True,
    )

    senha_hash = Column(
        String(255),
        nullable=False,
    )

    nome_completo = Column(
        String(120),
        nullable=False,
    )

    perfil = Column(
        String(30),
        nullable=False,
        default="profissional",
    )

    profissional = relationship(
        "Profissional",
        back_populates="usuario",
        uselist=False,
    )

    def __repr__(self):
        return (
            f"<Usuario "
            f"id={self.id} "
            f"username={self.username!r} "
            f"perfil={self.perfil!r}>"
        )
