import os
import psycopg2
from psycopg2 import errors
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv(encoding='cp1252')

# Recuperation des parametres de configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "ObservIA")

# Dictionnaire de connexion (sans la base cible pour la creation de la BDD)
CONN_PARAMS = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD
}


def create_database():
    """Se connecte a Postgres pour creer la base de donnees si elle n'existe pas."""
    print("Connexion au serveur PostgreSQL via les variables d'environnement...")
    
    conn = psycopg2.connect(**CONN_PARAMS, database="postgres")
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f'CREATE DATABASE "{DB_NAME}";')
        print(f"Base de donnees '{DB_NAME}' creee avec succes !")
    except errors.DuplicateDatabase:
        print(f"La base de donnees '{DB_NAME}' existe deja.")
    finally:
        cursor.close()
        conn.close()


def create_tables():
    """Se connecte a la base de donnees et cree toutes les tables du schema."""
    print(f"Connexion a la base '{DB_NAME}' pour generer les tables...")
    conn = psycopg2.connect(**CONN_PARAMS, database=DB_NAME)
    cursor = conn.cursor()

    # Liste des requetes SQL ordonnees selon les dependances du schema
    sql_queries = [
        # --- NIVEAU 1 : Tables totalement independantes ---
        """
        CREATE TABLE IF NOT EXISTS Competence (
            ID_Competence SERIAL PRIMARY KEY,
            nom_competence VARCHAR(255) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Localisation (
            code_Departement VARCHAR(5) PRIMARY KEY,
            nom_region VARCHAR(100),
            nom_departement VARCHAR(100),
            code_region VARCHAR(5)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS correspondance_rome_rncp (
            code_rome VARCHAR(5) PRIMARY KEY,
            intitule_rome VARCHAR(255)
        );
        """,
        
        # --- NIVEAU 2 : Tables dependantes du Niveau 1 ---
        """
        CREATE TABLE IF NOT EXISTS Siret (
            siret_of_contractant BIGINT PRIMARY KEY,
            nom_raison_social VARCHAR(255),
            code_Departement VARCHAR(5),
            FOREIGN KEY (code_Departement) REFERENCES Localisation(code_Departement) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Scraping (
            ID_Scraping SERIAL PRIMARY KEY,
            titre VARCHAR(255) NOT NULL,
            code_Departement VARCHAR(3),
            code_region VARCHAR(100),
            date_publication DATE,
            competence_tags VARCHAR(255),
            profil VARCHAR(255),
            FOREIGN KEY (code_Departement) REFERENCES Localisation(code_Departement) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Offre_France_travail (
            id_offre SERIAL PRIMARY KEY,                    -- Ton INT obligatoire pour tes autres tables
            id_francetravail VARCHAR(20) UNIQUE,          -- L'ID unique avec lettres (ex: '210HPPY')
            code_rome VARCHAR(5),
            code_departement VARCHAR(3),
            Competence VARCHAR(255),
            dateActualisation TIMESTAMP,
            dateCreation DATE,
            salaire VARCHAR(255),
            experience_exige VARCHAR(255)
            );
        """,
        """
        CREATE TABLE IF NOT EXISTS rncp_rome (
            code_rome VARCHAR(5),
            code_rncp INT,
            PRIMARY KEY (code_rome, code_rncp),
            FOREIGN KEY (code_rome) REFERENCES correspondance_rome_rncp(code_rome) ON DELETE CASCADE
        );
        """,
        
        # --- NIVEAU 3 : Tables dependantes du Niveau 2 & Tables Pivot ---
        """
        CREATE TABLE IF NOT EXISTS Csv_Formation (
            ID_formation SERIAL PRIMARY KEY,
            intitule_certification VARCHAR(255),
            entrees_formation INT,
            code_rncp INT,
            annee_mois DATE,
            siret_of_contractant BIGINT,
            FOREIGN KEY (siret_of_contractant) REFERENCES Siret(siret_of_contractant) ON DELETE SET NULL
        );
        """,
       """
        CREATE TABLE IF NOT EXISTS Offre_Competence (
            id_competence INT,
            id_francetravail VARCHAR(20),
            id_scraping INT DEFAULT 0,
            PRIMARY KEY (id_competence, id_francetravail, id_scraping),
            FOREIGN KEY (id_francetravail) REFERENCES Offre_France_travail(id_francetravail) ON DELETE CASCADE
        );
        """
    ]

    try:
        for query in sql_queries:
            cursor.execute(query)
        conn.commit()
        print("Structure relationnelle complete creee avec succes dans PostgreSQL !")
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la creation des tables : {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_database()
    create_tables()
    print("\nProcessus termine. Les tables ont ete configurees sur pgAdmin 4.")
