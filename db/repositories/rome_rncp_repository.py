"""Repository pour le modèle RomeRncp."""

import pandas as pd

from sqlalchemy.dialects.postgresql import insert

from db.session import SessionLocal
from db.models import RomeRncp

def insert_rome_rncp(df: pd.Dataframe) -> RomeRncp:
    """Insère les ROME/RNCP présents dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    with SessionLocal() as db:
        db.execute(insert(RomeRncp).on_conflict_do_nothing(), rows)
        db.commit()

def get_rome_rncp(
    code_rome: str | None = None,
    code_rncp: str | None = None,
) -> list[RomeRncp]:
    """Récupère les correspondances ROME/RNCP avec filtres optionnels."""
    with SessionLocal() as db:
        query = db.query(RomeRncp)

    if code_rome is not None:
        query = query.filter(RomeRncp.code_rome == code_rome)
    if code_rncp is not None:
        query = query.filter(RomeRncp.code_rncp == code_rncp)

    return query.all()
