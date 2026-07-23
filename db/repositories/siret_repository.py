"""Repository pour le modèle Siret."""

import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from db.models import Siret

def insert_siret(df: pd.Dataframe, db: Session) -> Siret:
    """Insère les régions présentes dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    db.execute(insert(Siret).on_conflict_do_nothing(), rows)
    db.commit()

def get_siret(
    db: Session,
    id_siret: int | None = None,
    name: str | None = None,
    id_region: str | None = None,
) -> list[Siret]:
    """Récupère les SIRET avec filtres optionnels."""
    query = db.query(Siret)

    if id_siret is not None:
        query = query.filter(Siret.id_siret == id_siret)
    if name is not None:
        query = query.filter(Siret.name == name)
    if id_region is not None:
        query = query.filter(Siret.id_region == id_region)

    return query.all()
