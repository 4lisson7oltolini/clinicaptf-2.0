"""
Model de Usuário do sistema (login da clínica).
A senha NUNCA é armazenada em texto puro — sempre como hash bcrypt.
"""
from sqlalchemy import Column, Integer, String

from database.connection import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome_completo = Column(String(120), nullable=False)

    def __repr__(self):
        return f"<Usuario id={self.id} username={self.username!r}>"