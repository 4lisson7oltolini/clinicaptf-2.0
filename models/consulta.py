"""
Model de Consulta: liga um Paciente a um Profissional em uma data/hora.
Este é o relacionamento central do domínio da clínica.
"""
from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates

from database.connection import Base

STATUS_VALIDOS = {"agendada", "confirmada", "concluida", "cancelada"}


class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(String(20), default="agendada", nullable=False)
    observacoes = Column(String(500), nullable=True)
    criado_em = Column(DateTime, default=datetime.now(UTC))

    paciente = relationship("Paciente")
    profissional = relationship("Profissional", back_populates="consultas")

    @validates("status")
    def _valida_status(self, key, value):
        if value not in STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {value}. Use um de {STATUS_VALIDOS}")
        return value

    def __repr__(self):
        return f"<Consulta id={self.id} paciente_id={self.paciente_id} data_hora={self.data_hora}>"