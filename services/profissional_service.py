from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.profissional import Profissional


class ProfissionalJaExisteError(Exception):
    pass


def criar_profissional(db: Session, nome: str, especialidade: str, registro_profissional: str) -> Profissional:
    profissional = Profissional(nome=nome, especialidade=especialidade, registro_profissional=registro_profissional)
    db.add(profissional)
    try:
        db.commit()
        db.refresh(profissional)
    except IntegrityError:
        db.rollback()
        raise ProfissionalJaExisteError(f"Já existe profissional com registro {registro_profissional}")
    return profissional


def listar_profissionais(db: Session) -> list[Profissional]:
    return db.query(Profissional).order_by(Profissional.nome).all()


def buscar_profissional_por_id(db: Session, profissional_id: int) -> Profissional | None:
    return db.query(Profissional).filter(Profissional.id == profissional_id).first()