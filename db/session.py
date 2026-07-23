"""
Gestion de la connexion SQLAlchemy à PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
import dotenv

dotenv.load_dotenv()

#DATABASE_URL = os.getenv("DATABASE_URL")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    """Classe de base pour les modèles SQLAlchemy."""

def get_db():
    """Dépendance FastAPI pour injecter une session BDD dans les routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()