"""Repository pour le modèle Skill."""

from sqlalchemy.dialects.postgresql import insert
from db.session import SessionLocal
from db.models import Skill


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
