import os
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Remonte d'un niveau (ObservIA) et va chercher dans results/sirets.csv
CSV_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "result", "sirets.csv"))
# CSV colonnes (par position) : 0=siret | 1=nom | 2=code_postal | 3=code_departement
# Table : siret_of_contractant (bigint PK) | nom_raison_social (varchar) | code_departement (varchar 5)

UPSERT_ROW = """
INSERT INTO siret (siret_of_contractant, nom_raison_social, code_departement)
VALUES (%s, %s, %s)
ON CONFLICT (siret_of_contractant)
DO UPDATE SET
    nom_raison_social = EXCLUDED.nom_raison_social,
    code_departement   = EXCLUDED.code_departement;
"""

COUNT_ROWS = "SELECT COUNT(*) FROM siret;"


def load_csv(path: str) -> list[tuple]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header
        for ligne in reader:
            siret     = int(ligne[0].strip())
            nom       = ligne[1].strip() or None
            code_dept = ligne[3].strip() or None  # on saute le code_postal (index 2)
            rows.append((siret, nom, code_dept))
    return rows


def import_sirets():
    print(f"Lecture de {CSV_PATH}...")
    rows = load_csv(CSV_PATH)
    print(f"{len(rows)} SIRETs charges.\n")

    print("Connexion a PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print(f"Connecte a '{DB_NAME}' sur {DB_HOST}:{DB_PORT}\n")

    try:
        print("Import des donnees en cours...")
        cursor.executemany(UPSERT_ROW, rows)
        conn.commit()

        cursor.execute(COUNT_ROWS)
        total = cursor.fetchone()[0]
        print(f"Import termine - {total} ligne(s) presentes dans 'siret'.\n")

    except Exception as e:
        conn.rollback()
        print(f"Erreur : {e}")

    finally:
        cursor.close()
        conn.close()
        print("Connexion fermee.")


if __name__ == "__main__":
    import_sirets()