"""
Création des tables de la base de données PostgreSQL.
"""
from db.session import engine, Base
from db import models

def create_database():
    """Crée toutes les tables définies dans models.py si elles n'existent pas."""
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")

if __name__ == "__main__":
    create_database()