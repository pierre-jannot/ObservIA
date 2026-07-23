"""
Routes d'affichage des données de formation.
"""

from fastapi import APIRouter, Query
from utils.compute_dataframe import get_filtered_values
from db.repositories.formation_repository import get_all_formations
from transformers.formations import add_zone_column
from indicators.formations import column_per_quarter

router = APIRouter()

@router.get("/all")
def get_all(limit: int = Query(50, le=500, description="Nombre max de résultats")):
    """
    Retourne toutes les formations présentes dans le fichier csv correspondant.

    Args:
        limit : int - Nombre d'offres retournées

    Returns:
        json - { result : formations }
    """
    dataframe = get_all_formations()
    dataframe = dataframe.head(limit)
    return {"result": dataframe.to_dict(orient="records")}

@router.get("/entry-per-quarter")
def get_formation_entry_per_quarter(
    id_region: list[str] | None = Query(None)
):
    """
    Retourne le nombre d'entrées en formation par trimestre.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions et départements utilisées pour filtrer

    Returns:
        json - { result : entrées en formation par trimestre }
    """
    dataframe = get_all_formations()
    if id_region:
        dataframe = add_zone_column(dataframe)
        dataframe = get_filtered_values(dataframe, "id_region", id_region)
    result = column_per_quarter(dataframe, "entries")
    return {"result": result}

@router.get("/exit-per-quarter")
def get_formation_exit_per_quarter(
    id_region: list[str] | None = Query(None)
):
    """
    Retourne le nombre de sorties de formation par trimestre.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions et départements utilisées pour filtrer

    Returns:
        json - { result : sorties de formation par trimestre }
    """
    dataframe = get_all_formations()
    if id_region:
        dataframe = add_zone_column(dataframe)
        dataframe = get_filtered_values(dataframe, "id_region", id_region)
    result = column_per_quarter(dataframe, "exits_full")
    return {"result": result}
