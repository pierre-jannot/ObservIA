import psycopg2
from psycopg2 import Extension, errors

# ⚙️ CONFIGURATION DE LA CONNEXION
CONN_PARAMS = {
    "host": "localhost",
    "port": "3455",          # Remplace par ton port (ex: 3455 ou 5432)
    "user": "postgres",
    "password": "TON_MOT_DE_PASSE_ICI"  # Mets ton vrai mot de passe
}
DB_NAME = "mon_projet_emploi"


def create_database():
    """Se connecte à Postgres pour créer la base de données si elle n'existe pas."""
    print("🔄 Connexion au serveur PostgreSQL...")
    # On se connecte à la base par défaut 'postgres' pour pouvoir créer la nouvelle base
    conn = psycopg2.connect(**CONN_PARAMS, database="postgres")
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"✅ Base de données '{DB_NAME}' créée avec succès !")
    except errors.DuplicateDatabase:
        print(f"ℹ️ La base de données '{DB_NAME}' existe déjà.")
    finally:
        cursor.close()
        conn.close()


def create_tables():
    """Se connecte à la nouvelle base de données et crée toutes les tables."""
    print(f"🔄 Connexion à la base '{DB_NAME}' pour créer les tables...")
    conn = psycopg2.connect(**CONN_PARAMS, database=DB_NAME)
    cursor = conn.cursor()

    # Définition des tables dans l'ordre de dépendance (très important pour les clés étrangères)
    sql_queries = [
        # --- Tables Indépendantes ---
        """
        CREATE TABLE IF NOT EXISTS Competence (
            ID_Competence SERIAL PRIMARY KEY,
            nom_competence VARCHAR(255) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Localisation (
            code_Departement VARCHAR(5) PRIMARY KEY,
            Region VARCHAR(100),
            Departement VARCHAR(100)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS correspondance_rome_rncp (
            code_rome VARCHAR(5)[] PRIMARY KEY,
            intitule_rome VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Siret (
            siret_of_contractant BIGINT PRIMARY KEY, -- BIGINT car les SIRET font 14 chiffres
            nom_raison_social VARCHAR(255),
            Region INT
        );
        """,
        # --- Tables Dépendantes (Niveau 1) ---
        """
        CREATE TABLE IF NOT EXISTS Scraping (
            ID_Scraping SERIAL PRIMARY KEY,
            titre VARCHAR(255) NOT NULL,
            code_region VARCHAR(3),
            date_publication DATE,
            competence_tags VARCHAR(255),
            profil VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Offre_France_travail (
            ID_FranceTravail SERIAL PRIMARY KEY,
            code_rome VARCHAR(5),
            code_Region VARCHAR(3),
            Competence VARCHAR(255),
            dateActualisation TIMESTAMP,
            dateCreation DATE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS rncp_rome (
            code_rome VARCHAR(5)[],
            code_rncp INT,
            PRIMARY KEY (code_rome, code_rncp),
            FOREIGN KEY (code_rome) REFERENCES correspondance_rome_rncp(code_rome) ON DELETE CASCADE
        );
        """,
        # --- Tables Dépendantes (Niveau 2 & Pivot) ---
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
            ID_Competence INT,
            ID_FranceTravail INT,
            ID_Scraping INT,
            PRIMARY KEY (ID_Competence, ID_FranceTravail, ID_Scraping),
            FOREIGN KEY (ID_Competence) REFERENCES Competence(ID_Competence) ON DELETE CASCADE,
            FOREIGN KEY (ID_FranceTravail) REFERENCES Offre_France_travail(ID_FranceTravail) ON DELETE CASCADE,
            FOREIGN KEY (ID_Scraping) REFERENCES Scraping(ID_Scraping) ON DELETE CASCADE
        );
        """
    ]

    try:
        for query in sql_queries:
            cursor.execute(query)
        conn.commit()
        print("🚀 Toutes les tables et clés composites ont été créées avec succès !")
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la création des tables : {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # 1. On crée d'abord la base de données
    create_database()
    # 2. On injecte les tables dedans
    create_tables()
    print("\n🏁 Processus terminé. Tu peux aller voir sur pgAdmin, tout est prêt !")