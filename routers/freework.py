"""
Routes d'affichage des offres Freework.
"""

from fastapi import APIRouter, Query

from utils.compute_dataframe import get_filtered_values, get_quarter_values, count_unique_values
from db.repositories.offers_repository import get_all_freework_offers
from transformers.locations import get_location_correspondance

router = APIRouter()

@router.get("/all")
def get_all(limit: int = Query(50, le=500, description="Nombre max de résultats")):
    """
    Retourne toutes les offres Freework présentes dans le fichier csv correspondant.

    Args:
        limit : int - Nombre d'offres retournées

    Returns:
        json - { result : nombre d'offres Freework }
    """
    dataframe = get_all_freework_offers()
    dataframe = dataframe.fillna("")
    dataframe = dataframe.head(limit)
    return {"result": dataframe.to_dict(orient="records")}

@router.get("/offers-per-quarter")
def get_offers_per_quarter(
    id_region: list[str] | None = Query(None)
):
    """
    Retourne le nombre d'offres Freework par trimestre.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions et départements utilisées pour filtrer

    Returns:
        json - { result : nombre d'offres Freework par trimestre }
    """
    dataframe = get_all_freework_offers()
    if id_region:
        dataframe = get_filtered_values(dataframe, "id_region", id_region)
    dataframe = get_quarter_values(dataframe, "pub_date")
    dataframe = count_unique_values(dataframe, "quarter")
    result = [
    {"trimestre": str(index), "nombre_offres_freework": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}

@router.get("/offers-per-region")
def get_offers_per_region():
    """
    Retourne le nombre d'offres Freework par région.

    Args:
        Pas d'arguments

    Returns:
        json - { result : nombre d'offres Freework par région }
    """
    dataframe = get_all_freework_offers()
    dataframe = get_location_correspondance(dataframe)
    dataframe = count_unique_values(dataframe, "location")
    result = [
    {"région": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}


@router.get("/offers-per-region/{id_region}")
def get_offers_per_chosen_region(id_region: str):
    """
    Retourne le nombre d'offres Freework par région.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions utilisées pour filtrer

    Returns:
        json - { result : nombre d'offres Freework par région }
    """
    dataframe = get_all_freework_offers()
    dataframe = get_filtered_values(dataframe, "id_region", [id_region])
    dataframe = get_location_correspondance(dataframe)
    dataframe = count_unique_values(dataframe, "region")
    result = [
    {"région": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}
