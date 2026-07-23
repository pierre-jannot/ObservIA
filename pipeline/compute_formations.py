"""
Fonctions de traitement et d'écriture en csv des données de formation.
"""

import os

import pandas as pd
from dotenv import load_dotenv

from extractors.init_csv_data import load_init_data
from extractors.location import scrap_locations_information
from transformers.formations import filter_data, prepare_formation_for_db
from transformers.sirets import get_sirets_information, prepare_siret_for_db
from transformers.locations import prepare_location_for_db
from transformers.rome import prepare_rome_for_db
from transformers.rome_rncp import prepare_rome_rncp_for_db
from utils.compute_dataframe import get_unique_values
from db.repositories.formation_repository import insert_formation
from db.repositories.region_repository import insert_region
from db.repositories.department_repository import insert_department
from db.repositories.siret_repository import insert_siret
from db.repositories.rome_repository import insert_rome
from db.repositories.rome_rncp_repository import insert_rome_rncp

load_dotenv()

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
E_S_FORMATIONS_PATH = f"{RESULT_PATH}/{os.getenv("E_S_FORMATIONS_PATH")}"
CORRESPONDANCES_PATH = f"{RESULT_PATH}/{os.getenv("CORRESPONDANCES_PATH")}"
SIRETS_PATH = f"{RESULT_PATH}/{os.getenv("SIRETS_PATH")}"
LOCATIONS_PATH = f"{RESULT_PATH}/{os.getenv("LOCATIONS_PATH")}"

def compute_formation_data(formations: pd.Dataframe, correspondances: pd.Dataframe):
    """
    Traitement et écriture des données de formation dans des fichiers csv.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    df_db_rome = prepare_rome_for_db(correspondances)
    df_db_rome_rncp = prepare_rome_rncp_for_db(correspondances)
    df_db_formation = prepare_formation_for_db(formations)
    insert_rome(df_db_rome)
    insert_rome_rncp(df_db_rome_rncp)
    insert_formation(df_db_formation)

def compute_sirets_information(formations: pd.DataFrame):
    """
    Récupère les identifiants SIRET uniques et les écrits dans un fichier csv.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    unique_sirets = get_unique_values(formations, "siret_of_contractant")
    sirets = pd.DataFrame(get_sirets_information(unique_sirets=unique_sirets))
    df_db = prepare_siret_for_db(sirets)
    insert_siret(df_db)

def compute_regions_information():
    """
    Réalise le scraping des données de départements et les écrits dans un fichier csv.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    locations = scrap_locations_information()
    df_db_region = prepare_location_for_db(locations, "region")
    df_db_department = prepare_location_for_db(locations, "department")
    insert_region(df_db_region)
    insert_department(df_db_department)

def compute_all():
    """
    Réalise le traitement des données de formation, SIRET et de départements.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    formations, correspondances = load_init_data()
    formations, correspondances = filter_data(formations, correspondances)
    compute_regions_information()
    compute_sirets_information(formations)
    compute_formation_data(formations, correspondances)
