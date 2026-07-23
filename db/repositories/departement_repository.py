"""Repository pour le modèle Departement."""

from sqlalchemy.orm import Session

from db.models import Departement


def insert_departement(db: Session, id_department: str, name_department: str, id_region: str) -> Departement:
    """Insère un département si il n'existe pas déjà."""
    existing = db.query(Departement).filter(Departement.id_department == id_department).first()
    if existing is not None:
        return existing

    departement = Departement(
        id_department=id_department,
        name_department=name_department,
        id_region=id_region,
    )
    db.add(departement)
    db.commit()
    db.refresh(departement)
    return departement


def get_departement(
    db: Session,
    id_department: str | None = None,
    name_department: str | None = None,
    id_region: str | None = None,
) -> list[Departement]:
    """Récupère les départements avec filtres optionnels."""
    query = db.query(Departement)

    if id_department is not None:
        query = query.filter(Departement.id_department == id_department)
    if name_department is not None:
        query = query.filter(Departement.name_department == name_department)
    if id_region is not None:
        query = query.filter(Departement.id_region == id_region)

    return query.all()
