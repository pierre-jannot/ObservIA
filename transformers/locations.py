"""
Transformeurs permettant la récupération du code régional.
"""

import re
import json
import time
import os
import pandas as pd

import requests
from dotenv import load_dotenv

from db.repositories.region_repository import get_locations

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT")
}

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
LOCATIONS_PATH = f"{RESULT_PATH}/{os.getenv("LOCATIONS_PATH")}"
LOCATION_BASE_URL = os.getenv("LOCATION_BASE_URL")

COLONNES_MAPPING_REGION = {
    "code_region":          "id_region",
    "nom_region":           "name_region",
}

COLONNES_DB_REGION = list(COLONNES_MAPPING_REGION.values())

COLONNES_MAPPING_DEPARTMENT = {
    "code_region":          "id_region",
    "code_departement":     "id_department",
    "nom_departement":      "name_department",
}

COLONNES_DB_DEPARTMENT = list(COLONNES_MAPPING_DEPARTMENT.values())

def prepare_location_for_db(df: pd.DataFrame, location_type: str) -> pd.DataFrame:
    """
    Renomme et sélectionne les colonnes du DataFrame location
    pour correspondre au schéma de la table PostgreSQL.

    Args:
        df: DataFrame brut issu du CSV MonCompteFormation.

    Returns:
        DataFrame prêt pour l'insertion en base.
    """
    if location_type == "region":
        df = df.rename(columns=COLONNES_MAPPING_REGION)
        df = df[COLONNES_DB_REGION]
    elif location_type == "department":
        df = df.rename(columns=COLONNES_MAPPING_DEPARTMENT)
        df = df[COLONNES_DB_DEPARTMENT]
    df = df.where(pd.notna(df), None)
    return df

def normalize_address(adresse: str) -> str:
    """
    Normalise le format de l'adresse donnée en paramètres.

    Args:
        adresse : str - Adresse brute

    Returns:
        str - Adresse normalisée
    """
    adresse = adresse.lower()
    mots = re.split(r"[^a-z0-9àâäéèêëïîôöùûüç]+", adresse)
    mots = [m for m in mots if m]
    return "+".join(mots)

def get_region(locations):
    """
    Renvoie la région de l'adresse donnée.

    Args:
        locations : str - Adresse

    Returns:
        str - Région
    """
    if locations is None:
        return None
    if locations == "France":
        return "11"
    locations_list = locations.split(", ")
    zones = get_locations()
    for location in locations_list:
        if location in zones["name_department"].values:
            return code_from_name(zones, location, "department")
        if location in zones["name_region"].values:
            return code_from_name(zones, location, "region")

    address = normalize_address(locations)
    url = f"{LOCATION_BASE_URL}/?q={address}"

    response = requests.get(url,
                            headers=HEADERS,
                            timeout=10).text
    time.sleep(0.3)

    data = json.loads(response)
    result = None

    if data.get("features"):
        try:
            correspondance = dict(zip(zones["id_department"], zones["id_region"]))
            depcode = data["features"][0]["properties"]["depcode"]
            result = correspondance.get(depcode, None)
        except (KeyError, IndexError, AttributeError, TypeError):
            return None
    return result


def code_from_name(zones, name, zone_type):
    """
    Retourne le code région.

    Args:
        zones : Dataframe - Table des départements et régions
        name : str - Nom du département ou de la région
        zone_type : str - Région

    Returns:
        str - Adresse normalisée
    """

    resultat = zones[zones[f"name_{zone_type}"] == name][f"id_region"]
    if resultat.empty:
        return None  # ou raise une exception explicite selon votre besoin

    return resultat.iloc[0]

def code_from_code(code):
    """
    Retourne le code région.

    Args:
        code : str - Code du département

    Returns:
        str - Adresse normalisée
    """

    locations = get_locations()
    resultat = locations[locations[f"id_department"] == code][f"id_region"]
    if resultat.empty:
        return None  # ou raise une exception explicite selon votre besoin

    return resultat.iloc[0]

def get_location_correspondance(dataframe):
    """
    Ajoute une colonne location avec le nom de la région correspondante.

    Args:
        dataframe : Dataframe - Dataframe contenant une colonne id_region

    Returns:
        dataframe : Dataframe - Dataframe avec la nouvelle colonne location
    """
    locations = get_locations()
    correspondance = dict(zip(locations["id_region"], locations["name_region"]))
    dataframe["location"] = dataframe["id_region"].map(correspondance).fillna(dataframe["id_region"])
    return dataframe