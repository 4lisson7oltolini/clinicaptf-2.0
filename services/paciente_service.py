"""
Camada de serviço: regras de negócio de Paciente, isolada da UI (Streamlit)
e do acesso a dados bruto. As pages/ chamam isso, nunca o model diretamente.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.paciente import Paciente


class PacienteJaExisteError(Exception):
    pass


def criar_paciente(db: Session, nome: str, cpf: str, cep: str, telefone: str | None = None) -> Paciente:
    paciente = Paciente(nome=nome, cpf=cpf, cep=cep, telefone=telefone)
    db.add(paciente)
    try:
        db.commit()
        db.refresh(paciente)
    except IntegrityError:
        db.rollback()
        raise PacienteJaExisteError(f"Já existe paciente com CPF {cpf}")
    return paciente


def listar_pacientes(db: Session, termo_busca: str | None = None) -> list[Paciente]:
    query = db.query(Paciente)
    if termo_busca:
        query = query.filter(Paciente.nome.ilike(f"%{termo_busca}%"))
    return query.order_by(Paciente.nome).all()


def buscar_por_id(db: Session, paciente_id: int) -> Paciente | None:
    return db.query(Paciente).filter(Paciente.id == paciente_id).first()


def remover_paciente(db: Session, paciente_id: int) -> bool:
    paciente = buscar_por_id(db, paciente_id)
    if not paciente:
        return False
    db.delete(paciente)
    db.commit()
    return True