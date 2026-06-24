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
CSV_PATH    = os.getenv("FORMATIONS_PATH", "results/formations.csv")

# CSV : annee_mois ; code_rncp ; intitule_certification ; siret_of_contractant ; entrees_formation
# Table : id_formation (serial PK auto) | intitule_certification | entrees_formation | code_rncp | annee_mois | siret_of_contractant

INSERT_ROW = """
INSERT INTO csv_formation (intitule_certification, entrees_formation, code_rncp, annee_mois, siret_of_contractant)
VALUES (%s, %s, %s, %s, %s);
"""

COUNT_ROWS = "SELECT COUNT(*) FROM csv_formation;"


def parse_date(value: str) -> str | None:
    """Convertit '2025-01' en '2025-01-01' pour PostgreSQL (type date)."""
    value = value.strip()
    if not value:
        return None
    if len(value) == 7:  # format YYYY-MM
        return value + "-01"
    return value


def load_csv(path: str) -> list[tuple]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for ligne in reader:
            intitule  = ligne["intitule_certification"].strip() or None
            entrees   = int(ligne["entrees_formation"]) if ligne["entrees_formation"].strip() else None
            code_rncp = int(ligne["code_rncp"]) if ligne["code_rncp"].strip() else None
            date      = parse_date(ligne["annee_mois"])
            siret     = int(ligne["siret_of_contractant"]) if ligne["siret_of_contractant"].strip() else None
            rows.append((intitule, entrees, code_rncp, date, siret))
    return rows


def import_formations():
    print(f"Lecture de {CSV_PATH}...")
    rows = load_csv(CSV_PATH)
    print(f"    {len(rows)} formations chargées.\n")

    print("Connexion à PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print(f"    Connecté à '{DB_NAME}' sur {DB_HOST}:{DB_PORT}\n")

    try:
        print("Import des données en cours...")
        cursor.executemany(INSERT_ROW, rows)
        conn.commit()

        cursor.execute(COUNT_ROWS)
        total = cursor.fetchone()[0]
        print(f"Import terminé — {total} ligne(s) présentes dans 'csv_formation'.\n")

    except Exception as e:
        conn.rollback()
        print(f"Erreur : {e}")

    finally:
        cursor.close()
        conn.close()
        print("Connexion fermée.")


if __name__ == "__main__":
    import_formations()