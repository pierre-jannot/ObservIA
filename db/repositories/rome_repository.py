"""Repository pour le modèle Rome."""

import pandas as pd

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db.session import SessionLocal
from db.models import Rome

def insert_rome(df: pd.DataFrame) -> Rome:
    """Insère les ROME présents dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    with SessionLocal() as db:
        db.execute(insert(Rome).on_conflict_do_nothing(), rows)
        db.commit()

def get_rome(
    code_rome: str | None = None,
    rome_name: str | None = None,
) -> list[Rome]:
    """Récupère les codes ROME avec filtres optionnels."""
    with SessionLocal() as db:
        query = db.query(Rome)

    if code_rome is not None:
        query = query.filter(Rome.code_rome == code_rome)
    if rome_name is not None:
        query = query.filter(Rome.rome_name == rome_name)

    return query.all()

def get_rome_codes() -> list[str]:
    with SessionLocal() as db:
        stmt = select(Rome.code_rome)
        return db.execute(stmt).scalars().all()
