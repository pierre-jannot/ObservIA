"""Repository pour le modèle Formation."""
import pandas as pd

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db.session import SessionLocal
from db.models import Formation

def insert_formation(df: pd.DataFrame) -> dict:
    """
    Insère un DataFrame de formations en ne gardant que les colonnes
    correspondant aux colonnes de la table PostgreSQL.

    Args:
        df: DataFrame nettoyé issu du pipeline formations.
        db: Session SQLAlchemy.

    Returns:
        Dictionnaire avec le nombre de lignes insérées et ignorées.
    """
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    with SessionLocal() as db:
        db.execute(insert(Formation), rows)
        db.commit()

def get_formation(
    formation_id: int | None = None,
    id_siret: int | None = None,
    code_rncp: str | None = None,
    title: str | None = None,
    year_month: str | None = None,
    region: str | None = None,
) -> list[Formation]:
    """Récupère les formations avec filtres optionnels."""
    with SessionLocal() as db:
        query = db.query(Formation)

    if formation_id is not None:
        query = query.filter(Formation.id == formation_id)
    if id_siret is not None:
        query = query.filter(Formation.id_siret == id_siret)
    if code_rncp is not None:
        query = query.filter(Formation.code_rncp == code_rncp)
    if title is not None:
        query = query.filter(Formation.title == title)
    if year_month is not None:
        query = query.filter(Formation.year_month == year_month)
    if region is not None:
        query = query.filter(Formation.region == region)

    return query.all()

def get_all_formations() -> pd.DataFrame:
    """Récupère toutes les formations."""
    with SessionLocal() as db:
        stmt = select(*Formation.__table__.columns)
        result = db.execute(stmt).mappings().all()
        return pd.DataFrame(result)

from sqlalchemy import select, func, String
import pandas as pd

def get_unique_formations() -> pd.DataFrame:
    with SessionLocal() as db:
        stmt = (
            select(
                Formation.id,
                Formation.title,
                Formation.code_rncp,
            )
            .where(
                Formation.title.is_not(None),
                func.trim(Formation.title) != "",
                Formation.code_rncp.is_not(None),
                func.trim(Formation.code_rncp.cast(String)) != "",
            )
            .distinct(Formation.code_rncp)
            .order_by(
                Formation.code_rncp,
                func.length(Formation.title).desc(),
            )
        )

        return pd.DataFrame(db.execute(stmt).mappings().all())
