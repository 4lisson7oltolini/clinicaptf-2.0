"""
Script único: cria o primeiro usuário admin do sistema.
Rodar com: python create_admin.py
"""
from database.connection import SessionLocal, init_db
from services.auth_service import criar_usuario, UsuarioJaExisteError

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    username = input("Usuário: ").strip()
    senha = input("Senha: ").strip()
    nome_completo = input("Nome completo: ").strip()

    try:
        criar_usuario(db, username=username, senha=senha, nome_completo=nome_completo)
        print(f"Usuário '{username}' criado com sucesso.")
    except UsuarioJaExisteError as erro:
        print(f"Erro: {erro}")
    finally:
        db.close()