import os
import csv
import psycopg2
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# Chargement des variables d'environnement
# ─────────────────────────────────────────────
load_dotenv()

DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Remonte d'un niveau (ObservIA) et va chercher dans results/sirets.csv
CSV_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "results", "departments.csv"))
# ─────────────────────────────────────────────
# Requêtes SQL
# ─────────────────────────────────────────────

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS localisation (
    code_departement VARCHAR(3)   PRIMARY KEY,
    nom_departement  VARCHAR(100) NOT NULL,
    nom_region       VARCHAR(100) NOT NULL
);
"""

UPSERT_ROW = """
INSERT INTO localisation (code_departement, nom_departement, nom_region)
VALUES (%s, %s, %s)
ON CONFLICT (code_departement)
DO UPDATE SET
    nom_departement = EXCLUDED.nom_departement,
    nom_region       = EXCLUDED.nom_region;
"""

COUNT_ROWS = "SELECT COUNT(*) FROM localisation;"


def load_csv(path: str) -> list[tuple]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for ligne in reader:
            rows.append((
                ligne["code_departement"].strip(),
                ligne["nom_departement"].strip(),
                ligne["region"].strip(),
            ))
    return rows


def import_departments():
    print(f"Lecture de {CSV_PATH}...")
    rows = load_csv(CSV_PATH)
    print(f"    {len(rows)} départements chargés.\n")

    print("Connexion à PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print(f"Connecté à '{DB_NAME}' sur {DB_HOST}:{DB_PORT}\n")

    try:
        print("Création de la table si elle n'existe pas...")
        cursor.execute(CREATE_TABLE)

        print("Import des données en cours...")
        cursor.executemany(UPSERT_ROW, rows)

        conn.commit()

        cursor.execute(COUNT_ROWS)
        total = cursor.fetchone()[0]
        print(f"Import terminé — {total} ligne(s) présentes dans 'localisation'.\n")

    except Exception as e:
        conn.rollback()
        print(f"Erreur pendant l'import : {e}")

    finally:
        cursor.close()
        conn.close()
        print("Connexion fermée.")


if __name__ == "__main__":
    import_departments()