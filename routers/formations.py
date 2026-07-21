"""
Routes d'affichage des données de formation.
"""

from fastapi import APIRouter, Query
from utils.compute_dataframe import get_filtered_values
from extractors.formations import load_formations
from transformers.zone_normalizer import add_zone_column
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
    dataframe = load_formations()
    dataframe = dataframe.head(limit)
    return {"result": dataframe.to_dict(orient="records")}

@router.get("/entry-per-quarter")
def get_formation_entry_per_quarter(
    zone: list[str] | None = Query(None)
):
    """
    Retourne le nombre d'entrées en formation par trimestre.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions et départements utilisées pour filtrer

    Returns:
        json - { result : entrées en formation par trimestre }
    """
    dataframe = load_formations()
    if zone:
        dataframe = add_zone_column(dataframe)
        dataframe = get_filtered_values(dataframe, "zone", zone)
    result = column_per_quarter(dataframe, "entrees_formation")
    return {"result": result}

@router.get("/exit-per-quarter")
def get_formation_exit_per_quarter(
    zone: list[str] | None = Query(None)
):
    """
    Retourne le nombre de sorties de formation par trimestre.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions et départements utilisées pour filtrer

    Returns:
        json - { result : sorties de formation par trimestre }
    """
    dataframe = load_formations()
    if zone:
        dataframe = add_zone_column(dataframe)
        dataframe = get_filtered_values(dataframe, "zone", zone)
    result = column_per_quarter(dataframe, "sorties_realisation_totale")
    return {"result": result}
