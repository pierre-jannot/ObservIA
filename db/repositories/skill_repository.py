"""Repository pour le modèle Skill."""

from sqlalchemy.orm import Session

from db.models import Skill


def insert_skill(db: Session, source: str, name: str) -> Skill:
    """Insère une compétence si elle n'existe pas déjà."""
    existing = (
        db.query(Skill)
        .filter(Skill.source == source, Skill.name == name)
        .first()
    )

    if existing is not None:
        return existing

    skill = Skill(source=source, name=name)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def get_skill(
    db: Session,
    skill_id: int | None = None,
    source: str | None = None,
    name: str | None = None,
) -> list[Skill]:
    """Récupère les compétences avec filtres optionnels."""
    query = db.query(Skill)

    if skill_id is not None:
        query = query.filter(Skill.id == skill_id)
    if source is not None:
        query = query.filter(Skill.source == source)
    if name is not None:
        query = query.filter(Skill.name == name)

    return query.all()
