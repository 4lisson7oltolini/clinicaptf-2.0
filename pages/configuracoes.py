"""
Configurações centrais da aplicação.
Carrega variáveis de ambiente do .env (nunca hardcode credenciais no código).
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./clinicaptf.db",  # fallback local para dev sem Postgres
)
APP_ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")