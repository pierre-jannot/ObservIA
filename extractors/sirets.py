import os
import time

from dotenv import load_dotenv
import requests

from utils.compute_dataframe import load_csv_to_df

load_dotenv()

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
SIRETS_PATH = f"{RESULT_PATH}/{os.getenv("SIRETS_PATH")}"
SIRETS_BASE_URL = os.getenv("SIRETS_BASE_URL")

def load_sirets():
    sirets = load_csv_to_df(SIRETS_PATH)
    return sirets

def get_department_from_siret(siret: str) -> dict:
    r = requests.get(
        SIRETS_BASE_URL,
        params={"q": siret, "mtm_campaign": "annuaire"}
    )
    while r.status_code == 429:
        time.sleep(1)
        r = requests.get(
            SIRETS_BASE_URL,
            params={"q": siret, "mtm_campaign": "annuaire"}
        )
    result = r.json()["results"][0]
    siege = result["siege"]
    return {
        "siret": siret,
        "nom_raison_sociale": result["nom_raison_sociale"],
        "code_postal": siege["code_postal"],
        "location": f"D{siege['departement']}",
    }
