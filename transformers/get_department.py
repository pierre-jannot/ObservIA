import pandas as pd
import re
import requests
import json
import time

HEADERS = {"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )}

def normalize_address(adresse: str) -> str:
    adresse = adresse.lower()
    mots = re.split(r"[^a-z0-9àâäéèêëïîôöùûüç]+", adresse)
    mots = [m for m in mots if m]
    return "+".join(mots)

def get_department(locations):
    if locations is None:
        return("")
    elif locations == "France":
        return("Île-de-France")
    locations_list = locations.split(", ")

    departments = pd.read_csv("result/departments.csv", sep=";", dtype=str)
    for location in locations_list:
        if location in departments["nom_departement"].values:   
            return(location)
        else:
            if location in departments["nom_region"].values:
                return(location)
    else:
        address = normalize_address(locations)
        url = "https://api-adresse.data.gouv.fr/search/?q=" + address

        response = requests.get(url, headers=HEADERS).text
        time.sleep(0.3)

        data = json.loads(response)

        if data["features"]:
            try:
                correspondance = dict(zip(departments["code_departement"], departments["nom_departement"]))
                return(correspondance[data["features"][0]["properties"]["context"].split(',')[0]])
            except:
                return("")
        else:
            return("")
