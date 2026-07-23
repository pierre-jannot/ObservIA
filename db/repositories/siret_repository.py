"""Repository pour le modèle Siret."""

import pandas as pd

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db.session import SessionLocal
from db.models import Siret

def insert_siret(df: pd.Dataframe) -> Siret:
    """Insère les régions présentes dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    with SessionLocal() as db:
        db.execute(insert(Siret).on_conflict_do_nothing(), rows)
        db.commit()

def get_siret(
    id_siret: int | None = None,
    name: str | None = None,
    id_region: str | None = None,
) -> list[Siret]:
    """Récupère les SIRET avec filtres optionnels."""
    with SessionLocal() as db:
        query = db.query(Siret)

    if id_siret is not None:
        query = query.filter(Siret.id_siret == id_siret)
    if name is not None:
        query = query.filter(Siret.name == name)
    if id_region is not None:
        query = query.filter(Siret.id_region == id_region)

    return query.all()

def get_all_sirets() -> pd.DataFrame:
    """Récupère toute la table sirets."""
    with SessionLocal() as db:
        stmt = select(Siret.__table__.columns)
        result = db.execute(stmt).mappings().all()
        return pd.DataFrame(result)
