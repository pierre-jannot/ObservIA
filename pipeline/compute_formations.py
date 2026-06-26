import os
import pandas as pd
from dotenv import load_dotenv
from extractors.init_csv_data import load_init_data
from extractors.departments import scrap_departments_information
from transformers.rome_rncp_filtering import filter_data
from transformers.siret_information import get_sirets_information
from utils.write_to_csv import write_dataframe
from utils.create_folder import create_folder
from utils.compute_dataframe import get_unique_values

load_dotenv()

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
FORMATIONS_PATH = f"{RESULT_PATH}/{os.getenv("FORMATIONS_PATH")}"
CORRESPONDANCES_PATH = f"{RESULT_PATH}/{os.getenv("CORRESPONDANCES_PATH")}"
SIRETS_PATH = f"{RESULT_PATH}/{os.getenv("SIRETS_PATH")}"
DEPARTMENTS_PATH = f"{RESULT_PATH}/{os.getenv("DEPARTMENTS_PATH")}"

def compute_formation_data():
    create_folder(RESULT_PATH)
    if os.path.exists(FORMATIONS_PATH) and os.path.exists(CORRESPONDANCES_PATH):
        print(f"Données {FORMATIONS_PATH} et {CORRESPONDANCES_PATH} existantes. Réécriture des données ignorée.")
        return
    else:
        formations, correspondances = load_init_data()
        formations, correspondances = filter_data(formations=formations, correspondances=correspondances)
        write_dataframe(path=FORMATIONS_PATH, dataframe=formations)
        write_dataframe(path=CORRESPONDANCES_PATH, dataframe=correspondances)

def compute_sirets_information():
    if os.path.exists(SIRETS_PATH):
        print(f"Données {SIRETS_PATH} existantes. Réécriture des données ignorée.")
        return
    else:
        formations = pd.read_csv(FORMATIONS_PATH, sep=";", encoding="utf-8")
        unique_sirets = get_unique_values(formations, "siret_of_contractant")
        sirets_information = pd.DataFrame(get_sirets_information(unique_sirets=unique_sirets))
        write_dataframe(path=SIRETS_PATH, dataframe=sirets_information)

def compute_departments_information():
    if os.path.exists(DEPARTMENTS_PATH):
        print(f"Données {DEPARTMENTS_PATH} existantes. Réécriture des données ignorée.")
        return
    else:
        departments = scrap_departments_information()
        write_dataframe(path=DEPARTMENTS_PATH, dataframe=departments)

def compute_all():
    compute_formation_data()
    compute_departments_information()
    compute_sirets_information()
    return