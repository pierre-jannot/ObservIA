import os
import pandas as pd
from dotenv import load_dotenv
from extractors.esf_csv import load_csv_data
from transformers.rome_rncp_filtering import filter_data
from transformers.siret_information import get_sirets_information
from utils.write_to_csv import write_dataframe
from utils.create_folder import create_folder
from utils.compute_dataframe import get_unique_values

load_dotenv()

result_path = os.getenv("RESULT_FOLDER_PATH")
formations_path = os.getenv("FORMATIONS_PATH")
correspondances_path = os.getenv("CORRESPONDANCES_PATH")
sirets_path = os.getenv("SIRETS_PATH")

def compute_formation_data():
    create_folder(result_path)
    if os.path.exists(formations_path) and os.path.exists(correspondances_path):
        print(f"Données {formations_path} et {correspondances_path} existantes. Réécriture des données ignorée.")
        return
    else:
        formations, correspondances = load_csv_data()
        formations, correspondances = filter_data(formations=formations, correspondances=correspondances)
        write_dataframe(path=formations_path, dataframe=formations)
        write_dataframe(path=correspondances_path, dataframe=correspondances)

def compute_sirets_informations():
    if os.path.exists(sirets_path):
        print(f"Données {sirets_path} existantes. Réécriture des données ignorée.")
        return
    else:
        formations = pd.read_csv(formations_path, sep=";", encoding="utf-8")
        unique_sirets = get_unique_values(formations, "siret_of_contractant")
        sirets_information = pd.DataFrame(get_sirets_information(unique_sirets=unique_sirets))
        write_dataframe(path=sirets_path, dataframe=sirets_information)
