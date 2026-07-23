"""Repository pour le modèle Region."""
import pandas as pd

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db.session import SessionLocal
from db.models import Region, Department


def insert_region(df: pd.Dataframe) -> Region:
    """Insère les régions présentes dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    with SessionLocal() as db:
        db.execute(insert(Region).on_conflict_do_nothing(), rows)
        db.commit()


def get_region(
    id_region: str | None = None,
    name_region: str | None = None,
) -> list[Region]:
    """Récupère les régions avec filtres optionnels."""
    with SessionLocal() as db:
        query = db.query(Region)

    if id_region is not None:
        query = query.filter(Region.id_region == id_region)
    if name_region is not None:
        query = query.filter(Region.name_region == name_region)

    return query.all()


def get_locations() -> pd.DataFrame:
    """Récupère la table complète des départements et régions."""

    stmt = select(
        Region.id_region,
        Region.name_region,
        Department.id_department,
        Department.name_department).outerjoin(Region.departments)

    with SessionLocal() as db:
        result = db.execute(stmt)

    df = pd.DataFrame(result.fetchall(), columns=result.keys())

    return df