import csv
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

CSV_PATH = os.getenv("SCRAPING_PATH", "result/freework_offers.csv")

CITY_TO_DEPARTMENT = {
    "aix-en-provence": "13",
    "bordeaux": "33",
    "chalon-sur-saone": "71",
    "chatillon": "92",
    "clichy": "92",
    "grenoble": "38",
    "la defense": "92",
    "le mans": "72",
    "lille": "59",
    "lyon": "69",
    "marseille": "13",
    "mass": "91",
    "massy": "91",
    "meudon": "92",
    "montpellier": "34",
    "nantes": "44",
    "niort": "79",
    "paris": "75",
    "rennes": "35",
    "roissy-en-france": "95",
    "sevres": "92",
    "strasbourg": "67",
    "toulouse": "31",
}

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS scraping (
    id_scraping SERIAL PRIMARY KEY,
    titre TEXT NOT NULL,
    code_departement VARCHAR(3),
    code_region VARCHAR(100),
    date_publication DATE,
    competence_tags TEXT,
    profil TEXT,
    FOREIGN KEY (code_departement) REFERENCES localisation(code_departement) ON DELETE SET NULL
);
"""

ALTER_TABLE = """
ALTER TABLE scraping
    ADD COLUMN IF NOT EXISTS code_departement VARCHAR(3),
    ADD COLUMN IF NOT EXISTS code_region VARCHAR(100),
    ALTER COLUMN code_region TYPE VARCHAR(100);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'scraping_code_departement_fkey'
    ) THEN
        ALTER TABLE scraping
        ADD CONSTRAINT scraping_code_departement_fkey
        FOREIGN KEY (code_departement)
        REFERENCES localisation(code_departement)
        ON DELETE SET NULL;
    END IF;
END $$;
"""

INSERT_ROW = """
INSERT INTO scraping (titre, code_departement, code_region, date_publication, competence_tags, profil)
SELECT %s, %s, %s, %s, %s, %s
WHERE NOT EXISTS (
    SELECT 1
    FROM scraping
    WHERE titre = %s
      AND code_departement IS NOT DISTINCT FROM %s
      AND code_region IS NOT DISTINCT FROM %s
      AND date_publication IS NOT DISTINCT FROM %s
      AND profil IS NOT DISTINCT FROM %s
)
RETURNING id_scraping;
"""

COUNT_ROWS = "SELECT COUNT(*) FROM scraping;"


def resolve_path(path: str) -> Path:
    csv_path = Path(path)
    if csv_path.is_absolute():
        return csv_path
    return PROJECT_ROOT / csv_path


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def normalize_key(value: str | None) -> str:
    value = clean(value) or ""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_value.lower()


def parse_date(value: str | None) -> str | None:
    value = clean(value)
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value.split("T", 1)[0] if "T" in value else value


def localisation_columns(cursor) -> tuple[str, str, list[str], list[str]] | None:
    """Retourne les colonnes utiles de localisation."""
    cursor.execute(
        """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE lower(table_name) IN ('localisation', 'localitation')
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY
            CASE lower(table_name)
                WHEN 'localisation' THEN 1
                ELSE 2
            END
        """
    )
    rows = cursor.fetchall()
    if not rows:
        return None

    tables: dict[str, dict[str, str]] = {}
    for table_name, column_name in rows:
        tables.setdefault(table_name, {})[column_name.lower()] = column_name

    selected_table = next(
        (
            table_name
            for table_name, columns in tables.items()
            if "code_departement" in columns
        ),
        None,
    )
    if not selected_table:
        return None

    columns = tables[selected_table]
    code_departement_column = columns["code_departement"]

    department_label_columns = [
        columns[name]
        for name in ("departement", "nom_departement", "department", "nom_department")
        if name in columns
    ]

    region_label_columns = [
        columns[name]
        for name in ("region", "nom_region")
        if name in columns
    ]
    code_region_column = columns.get("code_region")
    return (
        selected_table,
        code_departement_column,
        department_label_columns,
        region_label_columns,
        code_region_column,
    )


def load_localisation_lookup(cursor) -> dict:
    columns = localisation_columns(cursor)
    if not columns:
        print("Attention : table localisation/localitation introuvable ou sans code_departement.")
        return {
            "by_department": {},
            "by_region": {},
            "valid_departments": set(),
            "table": None,
            "code_column": None,
        }

    (
        table_name,
        code_departement_column,
        department_label_columns,
        region_label_columns,
        code_region_column,
    ) = columns
    selected_columns = [
        code_departement_column,
        *department_label_columns,
        *region_label_columns,
        code_region_column,
    ]
    if code_region_column:
        selected_columns.append(code_region_column)
    query = sql.SQL("SELECT {} FROM {}").format(
        sql.SQL(", ").join(sql.Identifier(column) for column in selected_columns),
        sql.Identifier(table_name),
    )
    cursor.execute(query)

    lookup = {
        "by_department": {},
        "by_region": {},
        "region_by_department": {},
        "valid_departments": set(),
        "table": table_name,
        "code_column": code_departement_column,
    }

    for values in cursor.fetchall():
        code_departement = clean(str(values[0]) if values[0] is not None else None)
        if not code_departement:
            continue

        next_index = 1
        department_values = values[next_index:next_index + len(department_label_columns)]
        next_index += len(department_label_columns)
        region_values = values[next_index:next_index + len(region_label_columns)]
        next_index += len(region_label_columns)

        # Utilise la colonne code_region directement si disponible
        if code_region_column and next_index < len(values):
            raw = values[next_index]
            code_region = clean(str(raw) if raw is not None else None)
        else:
            code_region = next(
                (
                    clean(str(v) if v is not None else None)
                    for v in region_values
                    if clean(str(v) if v is not None else None)
                ),
                None,
            )

        lookup["valid_departments"].add(code_departement)
        lookup["region_by_department"][code_departement] = code_region
        department_data = {
            "code_departement": code_departement,
            "code_region": code_region,
        }
        lookup["by_department"][normalize_key(code_departement)] = department_data

        for label in department_values:
            label = clean(str(label) if label is not None else None)
            if label:
                lookup["by_department"].setdefault(normalize_key(label), department_data)

        for label in region_values:
            label = clean(str(label) if label is not None else None)
            if label:
                lookup["by_region"].setdefault(normalize_key(label), code_region)

    print(
        f"Localisation utilisee : {table_name}.{code_departement_column} "
        f"({len(lookup['valid_departments'])} departement(s))."
    )
    return lookup


def department_from_postal_code(value: str | None, lookup: dict) -> str | None:
    value = clean(value)
    if not value:
        return None

    match = re.search(r"\b(\d{5})\b", value)
    if not match:
        return None

    postal_code = match.group(1)
    code_departement = postal_code[:3] if postal_code.startswith(("97", "98")) else postal_code[:2]
    if code_departement in lookup["valid_departments"]:
        return code_departement
    return None


def resolve_location(row: dict[str, str], lookup: dict) -> tuple[str | None, str | None]:
    values_to_try = []
    location = clean(row.get("location"))
    address = clean(row.get("address"))

    if location:
        values_to_try.append(location)

    if address:
        address_parts = [part.strip() for part in address.split(",") if part.strip()]
        values_to_try.extend(address_parts)

    for value in values_to_try:
        code_departement = department_from_postal_code(value, lookup)
        if code_departement:
            return code_departement, lookup["region_by_department"].get(code_departement)

    for value in values_to_try:
        department_data = lookup["by_department"].get(normalize_key(value))
        if department_data:
            return department_data["code_departement"], department_data["code_region"]

    for value in values_to_try:
        code_departement = CITY_TO_DEPARTMENT.get(normalize_key(value))
        if code_departement in lookup["valid_departments"]:
            return code_departement, lookup["region_by_department"].get(code_departement)

    for value in values_to_try:
        code_region = lookup["by_region"].get(normalize_key(value))
        if code_region:
            return None, code_region

    return None, None


def column_limits(cursor) -> dict[str, int]:
    cursor.execute(
        """
        SELECT lower(column_name), character_maximum_length
        FROM information_schema.columns
        WHERE lower(table_name) = 'scraping'
          AND character_maximum_length IS NOT NULL;
        """
    )
    return {name: limit for name, limit in cursor.fetchall()}


def truncate(value: str | None, limit: int | None) -> str | None:
    if value is None or limit is None:
        return value
    return value[:limit]


def load_csv(path: Path, lookup: dict, limits: dict[str, int]) -> list[tuple]:
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for line_number, line in enumerate(reader, start=2):
            title = clean(line.get("title"))
            if not title:
                print(f"Ligne {line_number} ignoree : titre manquant.")
                continue

            code_departement, code_region = resolve_location(line, lookup)
            date_publication = parse_date(line.get("publication_date"))
            competence_tags = clean(line.get("skill_tags"))
            profil = clean(line.get("profile"))

            title = truncate(title, limits.get("titre"))
            code_departement = truncate(code_departement, limits.get("code_departement"))
            code_region = truncate(code_region, limits.get("code_region"))
            competence_tags = truncate(competence_tags, limits.get("competence_tags"))
            profil = truncate(profil, limits.get("profil"))

            rows.append((title, code_departement, code_region, date_publication, competence_tags, profil))
    return rows


def import_scraping() -> None:
    csv_path = resolve_path(CSV_PATH)
    if not csv_path.exists():
        print(f"Erreur : fichier CSV introuvable : {csv_path}")
        return

    print("Connexion a PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print(f"Connecte a '{DB_NAME}' sur {DB_HOST}:{DB_PORT}")

    try:
        cursor.execute(CREATE_TABLE)
        cursor.execute(ALTER_TABLE)

        lookup = load_localisation_lookup(cursor)
        limits = column_limits(cursor)

        print(f"Lecture de {csv_path}...")
        rows = load_csv(csv_path, lookup, limits)
        print(f"{len(rows)} offre(s) chargee(s).")

        inserted = 0
        ignored = 0
        for row in rows:
            titre, code_departement, code_region, date_publication, competence_tags, profil = row
            cursor.execute(
                INSERT_ROW,
                (
                    titre,
                    code_departement,
                    code_region,
                    date_publication,
                    competence_tags,
                    profil,
                    titre,
                    code_departement,
                    code_region,
                    date_publication,
                    profil,
                ),
            )
            if cursor.fetchone():
                inserted += 1
            else:
                ignored += 1

        conn.commit()

        cursor.execute(COUNT_ROWS)
        total = cursor.fetchone()[0]
        print(f"Import termine : {inserted} inseree(s), {ignored} deja presente(s).")
        print(f"{total} ligne(s) presentes dans 'scraping'.")

    except Exception as exc:
        conn.rollback()
        print(f"Erreur pendant l'import : {exc}")

    finally:
        cursor.close()
        conn.close()
        print("Connexion fermee.")


if __name__ == "__main__":
    import_scraping()
