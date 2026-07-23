"""Repository pour le modèle Region."""
import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from db.models import Region


def insert_region(df: pd.Dataframe, db: Session) -> Region:
    """Insère les régions présentes dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    db.execute(insert(Region).on_conflict_do_nothing(), rows)
    db.commit()


def get_region(
    db: Session,
    id_region: str | None = None,
    name_region: str | None = None,
) -> list[Region]:
    """Récupère les régions avec filtres optionnels."""
    query = db.query(Region)

    if id_region is not None:
        query = query.filter(Region.id_region == id_region)
    if name_region is not None:
        query = query.filter(Region.name_region == name_region)

    return query.all()
