"""
Cria os dados iniciais do ambiente de demonstração do ClinicPTF 2.0.
"""

from database.connection import SessionLocal
from models import Paciente, Profissional, Usuario
from services.paciente_service import criar_paciente
from services.profissional_service import criar_profissional
from services.auth_service import criar_usuario, UsuarioJaExisteError


def criar_dados_demo():
    db = SessionLocal()

    try:
        # ==========================================
        # PACIENTES
        # ==========================================

        if not db.query(Paciente).first():

            criar_paciente(
                db,
                nome="Maria Silva",
                cpf="52998224725",
                cep="01311000",
                telefone="47999990001",
            )

            criar_paciente(
                db,
                nome="João Souza",
                cpf="11144477735",
                cep="20040002",
                telefone="47999990002",
            )

            criar_paciente(
                db,
                nome="Ana Costa",
                cpf="12345678909",
                cep="88010000",
                telefone="47999990003",
            )

            print("Pacientes de demonstração criados.")
        else:
            print("Pacientes de demonstração já existem.")

        # ==========================================
        # PROFISSIONAIS
        # ==========================================

        if not db.query(Profissional).first():

            criar_profissional(
                db,
                nome="Dra. Ana Oliveira",
                especialidade="Fisioterapia Ortopédica",
                registro_profissional="CREFITO-DEMO-001",
            )

            criar_profissional(
                db,
                nome="Dr. Carlos Mendes",
                especialidade="Fisioterapia Esportiva",
                registro_profissional="CREFITO-DEMO-002",
            )

            print("Profissionais de demonstração criados.")
        else:
            print("Profissionais de demonstração já existem.")

        # ==========================================
        # USUÁRIO DEMO
        # ==========================================

        usuario_demo = (
            db.query(Usuario)
            .filter(Usuario.username == "demo")
            .first()
        )

        if usuario_demo:
            print("Usuário demo já existe.")
        else:
            try:
                criar_usuario(
                    db,
                    username="demo",
                    senha="demo1234",
                    nome_completo="Usuário Demonstração",
                )

                print("Usuário demo criado com sucesso.")

            except UsuarioJaExisteError:
                print("Usuário demo já existe.")

        print()
        print("===================================")
        print("DADOS DE DEMONSTRAÇÃO PRONTOS")
        print("===================================")
        print("Usuário: demo")
        print("Senha:   demo1234")
        print("===================================")

    finally:
        db.close()


if __name__ == "__main__":
    criar_dados_demo()