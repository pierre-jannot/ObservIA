"""
Gestion de la connexion SQLAlchemy à PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
import dotenv

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

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