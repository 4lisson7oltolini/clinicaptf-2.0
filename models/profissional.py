"""
Model de Profissional (fisioterapeuta responsável pelas consultas).
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.connection import Base


class Profissional(Base):
    __tablename__ = "profissionais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    especialidade = Column(String(80), nullable=False)
    registro_profissional = Column(String(30), unique=True, nullable=False)  # ex: CREFITO

    consultas = relationship("Consulta", back_populates="profissional")

    def __repr__(self):
        return f"<Profissional id={self.id} nome={self.nome!r}>"