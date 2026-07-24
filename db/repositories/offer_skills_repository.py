"""Repository pour le modèle OfferSkill."""

from sqlalchemy.dialects.postgresql import insert
from db.session import SessionLocal
from db.models import OfferSkill


def insert_offer_skill_dict(offer_skill: dict) -> None:
    """
    Insère une offre_compétence au format dictionnaire.

    Args:
        offer: dict - Dictionnaire contenant l'offre_compétence.
    """
    with SessionLocal() as db:
        db.execute(insert(OfferSkill).values(**offer_skill).on_conflict_do_nothing())
        db.commit()
