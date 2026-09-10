"""
Model de Paciente usando SQLAlchemy ORM.
Substitui o SQL cru da v1 por uma camada tipada e testável.
"""
from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import validates

from database.connection import Base
from utils.validators import validar_cpf, validar_cep


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    cep = Column(String(8), nullable=False)
    telefone = Column(String(20), nullable=True)
    criado_em = Column(DateTime, default=datetime.now(UTC))

    @validates("cpf")
    def _valida_cpf(self, key, value):
        cpf_limpo = "".join(filter(str.isdigit, value))
        if not validar_cpf(cpf_limpo):
            raise ValueError(f"CPF inválido: {value}")
        return cpf_limpo

    @validates("cep")
    def _valida_cep(self, key, value):
        cep_limpo = "".join(filter(str.isdigit, value))
        if not validar_cep(cep_limpo):
            raise ValueError(f"CEP inválido: {value}")
        return cep_limpo

    def __repr__(self):
        return f"<Paciente id={self.id} nome={self.nome!r}>"