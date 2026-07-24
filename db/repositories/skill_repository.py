"""Repository pour le modèle Skill."""

import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from db.session import SessionLocal
from db.models import Skill, OfferSkill


def insert_skill_dict(skill: dict) -> None:
    """
    Insère une compétence au format dictionnaire.

    Args:
        offer: dict - Dictionnaire contenant la compétence.
    """
    with SessionLocal() as db:
        db.execute(insert(Skill).values(**skill).on_conflict_do_nothing())
        db.commit()

def get_skill(
    skill_id: int | None = None,
    source: str | None = None,
    name: str | None = None,
) -> list[Skill]:
    """Récupère les compétences avec filtres optionnels."""
    with SessionLocal() as db:
        query = db.query(Skill)

    if skill_id is not None:
        query = query.filter(Skill.id == skill_id)
    if source is not None:
        query = query.filter(Skill.source == source)
    if name is not None:
        query = query.filter(Skill.name == name)

    return query.all()

def get_all_skills():
    with SessionLocal() as db:
        stmt = (
            select(Skill.name)
        )

        return pd.DataFrame(db.execute(stmt).mappings().all())

def get_all_freework_skills():
    with SessionLocal() as db:
        stmt = (
            select(Skill.name)
            .where(Skill.source == "Freework")
        )

        return pd.DataFrame(db.execute(stmt).mappings().all())

def get_all_france_travail_skills():
    with SessionLocal() as db:
        stmt = (
            select(Skill.name)
            .where(Skill.source == "FranceTravail")
        )

        return pd.DataFrame(db.execute(stmt).mappings().all())

def get_top_skills(source: str):
    stmt = (
        select(
            OfferSkill.id_offer,
            Skill.name
        )
        .join(OfferSkill.skill)
        .where(Skill.source == source)
    )
    with SessionLocal() as db:
        return pd.DataFrame(db.execute(stmt).mappings().all())
