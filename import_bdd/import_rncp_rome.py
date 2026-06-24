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
CSV_PATH    = os.getenv("CORRESPONDANCES_PATH", "results/correspondances.csv")

# CSV colonnes (par position) : 0=code_rome | 1=intitule_rome | 2=code_rncp
# Table : code_rome (varchar[] PK) | code_rncp (integer PK)
# intitule_rome ignore : absent de la table

TRUNCATE_TABLE = "TRUNCATE TABLE rncp_rome;"

INSERT_ROW = """
INSERT INTO rncp_rome (code_rome, code_rncp)
VALUES (%s, %s);
"""

COUNT_ROWS = "SELECT COUNT(*) FROM rncp_rome;"


def load_csv(path: str) -> list[tuple]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        for ligne in reader:
            code_rome = ligne[0].strip()   # array PostgreSQL
            code_rncp = int(ligne[2].strip())
            rows.append((code_rome, code_rncp))
    return rows


def import_rncp_rome():
    print(f"Lecture de {CSV_PATH}...")
    rows = load_csv(CSV_PATH)
    print(f"{len(rows)} correspondances ROME-RNCP chargees.\n")

    print("Connexion a PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print(f"Connecte a '{DB_NAME}' sur {DB_HOST}:{DB_PORT}\n")

    try:
        print("Vidage de la table avant import...")
        cursor.execute(TRUNCATE_TABLE)

        print("Import des donnees en cours...")
        cursor.executemany(INSERT_ROW, rows)
        conn.commit()

        cursor.execute(COUNT_ROWS)
        total = cursor.fetchone()[0]
        print(f"Import termine - {total} ligne(s) presentes dans 'rncp_rome'.\n")

    except Exception as e:
        conn.rollback()
        print(f"Erreur : {e}")

    finally:
        cursor.close()
        conn.close()
        print("Connexion fermee.")


if __name__ == "__main__":
    import_rncp_rome()