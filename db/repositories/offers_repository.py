"""Repository pour le modèle Offers."""

import pandas as pd

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from db.session import SessionLocal
from db.models import Offer

def insert_offer(df: pd.DataFrame) -> dict:
    """
    Insère un DataFrame d'offres en ne gardant que les colonnes
    correspondant aux colonnes de la table PostgreSQL.

    Args:
        df: DataFrame nettoyé issu du pipeline formations.
    """
    df = df.replace({pd.NA: None, float("nan"): None})
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")

    with SessionLocal() as db:
        db.execute(insert(Offer).on_conflict_do_nothing(), rows)
        db.commit()


def insert_offer_dict(offer: dict) -> None:
    """
    Insère une offre au format dictionnaire.

    Args:
        offer: dict - Dictionnaire contenant l'offre.
    """
    with SessionLocal() as db:
        db.execute(insert(Offer).values(**offer).on_conflict_do_nothing())
        db.commit()


def get_offer(
    id_offer: str | None = None,
    source: str | None = None,
    title: str | None = None,
    id_region: str | None = None,
    rome_code: str | None = None,
) -> list[Offer]:
    """Récupère les offres avec filtres optionnels."""
    with SessionLocal() as db:
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

def get_all_freework_offers() -> pd.DataFrame:
    """Récupère toutes les formations."""
    with SessionLocal() as db:
        stmt = select(*Offer.__table__.columns).where(Offer.source == "Freework")
        result = db.execute(stmt).mappings().all()
        return pd.DataFrame(result)
    