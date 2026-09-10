"""
Models da aplicação ClinicPTF 2.0.

Este módulo centraliza o carregamento dos modelos SQLAlchemy.
"""

from models.paciente import Paciente
from models.profissional import Profissional
from models.consulta import Consulta
from models.usuario import Usuario

__all__ = [
    "Paciente",
    "Profissional",
    "Consulta",
    "Usuario",
]