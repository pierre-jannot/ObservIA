"""
Transformeurs permettant la récupération du code régional.
"""

import re
import json
import time
import os

import requests
from dotenv import load_dotenv

from utils.compute_dataframe import load_csv_to_df

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT")
}

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
LOCATIONS_PATH = f"{RESULT_PATH}/{os.getenv("LOCATIONS_PATH")}"
LOCATION_BASE_URL = os.getenv("LOCATION_BASE_URL")

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
        return ""
    if locations == "France":
        return "11"
    locations_list = locations.split(", ")

    zones = load_csv_to_df(LOCATIONS_PATH)
    for location in locations_list:
        if location in zones["nom_departement"].values:
            return code_from_name(zones, location, "departement")
        if location in zones["nom_region"].values:
            return code_from_name(zones, location, "region")

    address = normalize_address(locations)
    url = f"{LOCATION_BASE_URL}/?q={address}"

    response = requests.get(url,
                            headers=HEADERS,
                            timeout=10).text
    time.sleep(0.3)

    data = json.loads(response)
    result = ""

    if data["features"]:
        try:
            correspondance = dict(zip(zones["code_departement"], zones["code_region"]))
            result = correspondance[data["features"][0]["properties"]["depcode"]]
        except (KeyError, IndexError, AttributeError, TypeError) as e:
            return e
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

    resultat = zones[zones[f"nom_{zone_type}"] == name][f"code_region"]
    if resultat.empty:
        return None  # ou raise une exception explicite selon votre besoin

    return resultat.iloc[0]
