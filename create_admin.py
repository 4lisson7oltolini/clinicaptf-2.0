"""
Script único: cria o primeiro usuário admin do sistema.
Rodar com: python create_admin.py
"""
from database.connection import SessionLocal
from database.initialization import executar_migrations
from services.auth_service import (
    DadosUsuarioInvalidosError,
    UsuarioJaExisteError,
    criar_usuario,
)

if __name__ == "__main__":
    executar_migrations()
    db = SessionLocal()
    username = input("Usuário: ").strip()
    senha = input("Senha: ").strip()
    nome_completo = input("Nome completo: ").strip()

    try:
        criar_usuario(
            db,
            username=username,
            senha=senha,
            nome_completo=nome_completo,
            perfil="admin",
        )
        print(f"Usuário '{username}' criado com sucesso.")
    except UsuarioJaExisteError as erro:
        print(f"Erro: {erro}")
    except DadosUsuarioInvalidosError as erro:
        print(f"Dados inválidos: {erro}")
    finally:
        db.close()