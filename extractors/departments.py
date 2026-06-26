from utils.compute_dataframe import load_csv_to_df
from dotenv import load_dotenv

import os
import requests
import pandas as pd
import json

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT")
}

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
DEPARTMENTS_PATH = f"{RESULT_PATH}/{os.getenv("DEPARTMENTS_PATH")}"
DEPARTMENTS_BASE_URL = os.getenv("DEPARTMENTS_BASE_URL")
REGIONS_BASE_URL = os.getenv("REGIONS_BASE_URL")

def load_departments():
    departments = load_csv_to_df(DEPARTMENTS_PATH)
    return departments

def scrap_departments_information():
    response = requests.get(DEPARTMENTS_BASE_URL, headers=HEADERS).text
    departements = json.loads(response)

    response = requests.get(REGIONS_BASE_URL, headers=HEADERS).text
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
