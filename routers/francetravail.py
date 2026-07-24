import os
import psycopg2
from fastapi import APIRouter, Query
from dotenv import load_dotenv

from db.repositories.offers_repository import get_all_france_travail_offers
from db.repositories.skill_repository import get_top_skills
from utils.compute_dataframe import get_filtered_values, get_quarter_values, count_unique_values
from transformers.locations import get_location_correspondance

load_dotenv()

router = APIRouter()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "ObservIA")

def get_db_connection():

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@router.get("/all")
def get_all(limit: int = Query(50, le=500, description="Nombre max de résultats")):
    """
    Retourne toutes les offres France Travail présentes dans le fichier csv correspondant.

    Args:
        limit : int - Nombre d'offres retournées

    Returns:
        json - { result : nombre d'offres France Travail }
    """
    dataframe = get_all_france_travail_offers()
    dataframe = dataframe.fillna("")
    dataframe = dataframe.head(limit)
    return {"result": dataframe.to_dict(orient="records")}

@router.get("/offers-per-quarter")
def get_offers_per_quarter(
    id_region: list[str] | None = Query(None)
):
    """
    Retourne le nombre d'offres France Travail par trimestre.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions et départements utilisées pour filtrer

    Returns:
        json - { result : nombre d'offres France Travail par trimestre }
    """
    dataframe = get_all_france_travail_offers()
    if id_region:
        dataframe = get_filtered_values(dataframe, "id_region", id_region)
    dataframe = get_quarter_values(dataframe, "pub_date")
    dataframe = count_unique_values(dataframe, "quarter")
    result = [
    {"trimestre": str(index), "nombre_offres_france_travail": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}

@router.get("/offers-per-region")
def get_offers_per_region():
    """
    Retourne le nombre d'offres France Travail par région.

    Args:
        Pas d'arguments

    Returns:
        json - { result : nombre d'offres France Travail par région }
    """
    dataframe = get_all_france_travail_offers()
    dataframe = get_location_correspondance(dataframe)
    dataframe = count_unique_values(dataframe, "location")
    result = [
    {"région": index, "nombre_offres_france_travail": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}


@router.get("/offers-per-region/{id_region}")
def get_offers_per_chosen_region(id_region: str):
    """
    Retourne le nombre d'offres France Travail par région.
    Peut être filtré par un argument donnant une zone géographique.

    Args:
        zone : list[str] - Nom des régions utilisées pour filtrer

    Returns:
        json - { result : nombre d'offres France Travail par région }
    """
    dataframe = get_all_france_travail_offers()
    dataframe = get_filtered_values(dataframe, "id_region", [id_region])
    dataframe = get_location_correspondance(dataframe)
    dataframe = count_unique_values(dataframe, "location")
    result = [
    {"région": index, "nombre_offres_france_travail": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}

@router.get("/top-skills")
def show_top_skills():

    df = get_top_skills("FranceTravail")

    dataframe = (
        df["name"]
        .value_counts()
        .head(20)
    )

    result = [
        {
            "compétence": skill,
            "occurrences": int(count)
        }
        for skill, count in dataframe.items()
    ]

    return {"result": result}

