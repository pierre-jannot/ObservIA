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
        return ""
    if locations == "France":
        return "R11"
    locations_list = locations.split(", ")

    zones = load_csv_to_df(DEPARTMENTS_PATH)
    for location in locations_list:
        if location in zones["nom_departement"].values:
            return code_from_name(zones, location, "departement")
        if location in zones["nom_region"].values:
            return code_from_name(zones, location, "region")
        
    address = normalize_address(locations)
    url = f"{LOCATION_BASE_URL}/?q={address}"

    response = requests.get(url, headers=HEADERS).text
    time.sleep(0.3)

    data = json.loads(response)

    if data["features"]:
        try:
            correspondance = dict(zip(zones["code_departement"], zones["nom_departement"]))
            department = correspondance[data["features"][0]["properties"]["context"].split(',')[0]]
            result = f"D{department}"
            return result
        except:
            return ""
    else:
        return ""


def code_from_name(zones, name, zone_type):
    if zone_type == "departement":
        marker = "D"
    elif zone_type == "region":
        marker = "R"
    else:
        raise ValueError(f"zone_type inconnu : {zone_type}")

    resultat = zones[zones[f"nom_{zone_type}"] == name][f"code_{zone_type}"]
    if resultat.empty:
        return None  # ou raise une exception explicite selon votre besoin

    return f"{marker}{resultat.iloc[0]}"
