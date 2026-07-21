"""
Extraction des régions et départements depuis une page geo.api.gouv.
"""

import os
import json

from dotenv import load_dotenv
import requests
import pandas as pd

from utils.compute_dataframe import load_csv_to_df

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT")
}

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
DEPARTMENTS_PATH = f"{RESULT_PATH}/{os.getenv("DEPARTMENTS_PATH")}"
DEPARTMENTS_BASE_URL = os.getenv("DEPARTMENTS_BASE_URL")
REGIONS_BASE_URL = os.getenv("REGIONS_BASE_URL")

def load_departments():
    """
    Récupère les informations des départements et régions depuis le csv.

    Returns:
        departments : Dataframe pandas - Fichier departments.csv
    """
    departments = load_csv_to_df(DEPARTMENTS_PATH)
    return departments

def scrap_departments_information():
    """
    Scrapping des informations des départements et régions depuis une page geo.api.gouv.

    Returns:
        Dataframe pandas - Noms et codes des départements et régions
    """
    response = requests.get(DEPARTMENTS_BASE_URL,
                            headers=HEADERS,
                            timeout=10).text
    departements = json.loads(response)

    response = requests.get(REGIONS_BASE_URL,
                            headers=HEADERS,
                            timeout=10).text
    regions = json.loads(response)

    mapping_regions = {
        region["code"]: region["nom"]
        for region in regions
    }

    for departement in departements:
        departement["nomRegion"] = mapping_regions.get(
            departement["codeRegion"]
        )


    dataframe = pd.DataFrame(departements)

    dataframe = dataframe[["code", "nom", "codeRegion", "nomRegion"]]

    dataframe = dataframe.rename(columns={
        "nom": "nom_departement",
        "code": "code_departement",
        "codeRegion": "code_region",
        "nomRegion": "nom_region"
    })

    df_polynesie = pd.DataFrame([{
        "code_departement": "987",
        "nom_departement": "Polynésie française",
        "code_region": "987",
        "nom_region": "Polynésie française"
    }])

    dataframe = pd.concat([dataframe, df_polynesie], ignore_index=True)

    return dataframe
