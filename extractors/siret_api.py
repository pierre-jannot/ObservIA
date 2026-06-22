import requests
import os
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

DEPARTMENTS_PATH = os.getenv("DEPARTMENTS_PATH")

regions_table = {
    "84": "Auvergne-Rhône-Alpes",
    "27": "Bourgogne-Franche-Comté",
    "53": "Bretagne",
    "24": "Centre-Val de Loire",
    "94": "Corse",
    "44": "Grand Est",
    "32": "Hauts-de-France",
    "11": "Île-de-France",
    "28": "Normandie",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "52": "Pays de la Loire",
    "93": "Provence-Alpes-Côte d'Azur",
    "01": "Guadeloupe",
    "03": "Guyane",
    "02": "Martinique",
    "04": "La Réunion",
    "06": "Mayotte"
}

def get_region_from_siret(siret: str) -> dict:
    r = requests.get(
        "https://recherche-entreprises.api.gouv.fr/search",
        params={"q": siret, "mtm_campaign": "annuaire"}
    )
    result = r.json()["results"][0]
    siege = result["siege"]
    return {
        "siret": siret,
        "nom_raison_sociale": result["nom_raison_sociale"],
        "code_postal": siege["code_postal"],
        "region":      regions_table[siege["region"]],
    }

def get_department_from_siret(siret: str) -> dict:
    departments_df = pd.read_csv(DEPARTMENTS_PATH, sep=";", dtype=str)

    DEPARTMENT_TO_REGION = dict(
    zip(departments_df["identifiant_departement"], departments_df["nom_departement"])
    )

    r = requests.get(
        "https://recherche-entreprises.api.gouv.fr/search",
        params={"q": siret, "mtm_campaign": "annuaire"}
    )
    result = r.json()["results"][0]
    siege = result["siege"]
    return {
        "siret": siret,
        "nom_raison_sociale": result["nom_raison_sociale"],
        "code_postal": siege["code_postal"],
        "departement":      DEPARTMENT_TO_REGION[siege["departement"]],
    }