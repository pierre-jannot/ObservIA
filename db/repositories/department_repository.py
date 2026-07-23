"""Repository pour le modèle Departement."""

import pandas as pd

from db.session import SessionLocal
from db.models import Department, Region

from sqlalchemy.dialects.postgresql import insert


def insert_department(df: pd.Dataframe) -> Region:
    """Insère les régions présentes dans le dataframe"""
    df = df.where(pd.notna(df), None)
    rows = df.to_dict(orient="records")
    with SessionLocal() as db:
        db.execute(insert(Department).on_conflict_do_nothing(), rows)
        db.commit()


def get_department(
    id_department: str | None = None,
    name_department: str | None = None,
    id_region: str | None = None,
) -> list[Department]:
    """Récupère les départements avec filtres optionnels."""
    with SessionLocal() as db:
        query = db.query(Department)

    if id_department is not None:
        query = query.filter(Department.id_department == id_department)
    if name_department is not None:
        query = query.filter(Department.name_department == name_department)
    if id_region is not None:
        query = query.filter(Department.id_region == id_region)

    return query.all()
