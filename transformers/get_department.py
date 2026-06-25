import re
import requests
import json
import time
import os

from dotenv import load_dotenv
from utils.compute_dataframe import load_csv_to_df

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT")
}

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
DEPARTMENTS_PATH = f"{RESULT_PATH}/{os.getenv("DEPARTMENTS_PATH")}"
LOCATION_BASE_URL = os.getenv("LOCATION_BASE_URL")

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

    departments = load_csv_to_df(DEPARTMENTS_PATH)
    for location in locations_list:
        if location in departments["nom_departement"].values:   
            return(location)
        else:
            if location in departments["nom_region"].values:
                return(location)
    else:
        address = normalize_address(locations)
        url = f"{LOCATION_BASE_URL}/?q={address}"

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
