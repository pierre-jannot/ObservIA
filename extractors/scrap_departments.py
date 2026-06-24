import requests
import pandas as pd
import json

HEADERS = {"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )}

def scrap_departments_information():

    url = "https://geo.api.gouv.fr/departements"
    response = requests.get(url, headers=HEADERS).text
    departements = json.loads(response)

    url = "https://geo.api.gouv.fr/regions"
    response = requests.get(url, headers=HEADERS).text
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