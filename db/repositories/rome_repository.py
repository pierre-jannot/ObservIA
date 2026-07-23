"""Repository pour le modèle Rome."""

import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from db.models import Rome

def insert_rome(df: pd.Dataframe, db: Session) -> Rome:
    """Insère les ROME présents dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    db.execute(insert(Rome).on_conflict_do_nothing(), rows)
    db.commit()

def get_rome(
    db: Session,
    code_rome: str | None = None,
    rome_name: str | None = None,
) -> list[Rome]:
    """Récupère les codes ROME avec filtres optionnels."""
    query = db.query(Rome)

    if code_rome is not None:
        query = query.filter(Rome.code_rome == code_rome)
    if rome_name is not None:
        query = query.filter(Rome.rome_name == rome_name)

    return query.all()
