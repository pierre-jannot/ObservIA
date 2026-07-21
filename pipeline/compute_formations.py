"""
Fonctions de traitement et d'écriture en csv des données de formation.
"""

import os

import pandas as pd
from dotenv import load_dotenv

from extractors.init_csv_data import load_init_data
from extractors.location import scrap_locations_information
from transformers.rome_rncp_filtering import filter_data
from transformers.siret_information import get_sirets_information
from utils.write_to_csv import write_dataframe
from utils.create_folder import create_folder
from utils.compute_dataframe import get_unique_values

load_dotenv()

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
FORMATIONS_PATH = f"{RESULT_PATH}/{os.getenv("FORMATIONS_PATH")}"
CORRESPONDANCES_PATH = f"{RESULT_PATH}/{os.getenv("CORRESPONDANCES_PATH")}"
SIRETS_PATH = f"{RESULT_PATH}/{os.getenv("SIRETS_PATH")}"
LOCATIONS_PATH = f"{RESULT_PATH}/{os.getenv("LOCATIONS_PATH")}"

def compute_formation_data():
    """
    Traitement et écriture des données de formation dans des fichiers csv.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    create_folder(RESULT_PATH)
    if os.path.exists(FORMATIONS_PATH) and os.path.exists(CORRESPONDANCES_PATH):
        print(f"Données {FORMATIONS_PATH} existantes. Réécriture ignorée.")
        print(f"Données {CORRESPONDANCES_PATH} existantes. Réécriture ignorée.")
        return
    formations, correspondances = load_init_data()
    formations, correspondances = filter_data(formations, correspondances)
    write_dataframe(path=FORMATIONS_PATH, dataframe=formations)
    write_dataframe(path=CORRESPONDANCES_PATH, dataframe=correspondances)

def compute_sirets_information():
    """
    Récupère les identifiants SIRET uniques et les écrits dans un fichier csv.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    if os.path.exists(SIRETS_PATH):
        print(f"Données {SIRETS_PATH} existantes. Réécriture ignorée.")
        return
    formations = pd.read_csv(FORMATIONS_PATH, sep=";", encoding="utf-8")
    unique_sirets = get_unique_values(formations, "siret_of_contractant")
    sirets_information = pd.DataFrame(get_sirets_information(unique_sirets=unique_sirets))
    write_dataframe(path=SIRETS_PATH, dataframe=sirets_information)

def compute_regions_information():
    """
    Réalise le scraping des données de départements et les écrits dans un fichier csv.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    if os.path.exists(LOCATIONS_PATH):
        print(f"Données {LOCATIONS_PATH} existantes. Réécriture ignorée.")
        return
    departments = scrap_locations_information()
    write_dataframe(path=LOCATIONS_PATH, dataframe=departments)

def compute_all():
    """
    Réalise le traitement des données de formation, SIRET et de départements.

    Args:
        Pas d'arguments

    Returns:
        Pas de return
    """
    compute_formation_data()
    compute_regions_information()
    compute_sirets_information()
