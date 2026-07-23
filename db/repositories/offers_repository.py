"""Repository pour le modèle Offers."""

import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from db.models import Offer

def insert_offer(df: pd.DataFrame, db: Session) -> dict:
    """
    Insère un DataFrame d'offres en ne gardant que les colonnes
    correspondant aux colonnes de la table PostgreSQL.

    Args:
        df: DataFrame nettoyé issu du pipeline formations.
        db: Session SQLAlchemy.

    Returns:
        Dictionnaire avec le nombre de lignes insérées et ignorées.
    """
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    db.execute(insert(Offer).on_conflict_do_nothing(), rows)
    db.commit()


def get_offer(
    db: Session,
    id_offer: str | None = None,
    source: str | None = None,
    title: str | None = None,
    id_region: str | None = None,
    rome_code: str | None = None,
) -> list[Offer]:
    """Récupère les offres avec filtres optionnels."""
    query = db.query(Offer)

    if id_offer is not None:
        query = query.filter(Offer.id_offer == id_offer)
    if source is not None:
        query = query.filter(Offer.source == source)
    if title is not None:
        query = query.filter(Offer.title == title)
    if id_region is not None:
        query = query.filter(Offer.id_region == id_region)
    if rome_code is not None:
        query = query.filter(Offer.rome_code == rome_code)

    return query.all()
