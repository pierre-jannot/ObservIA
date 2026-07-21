"""
Lecture en dataframe des données de formation.
"""

import os

from dotenv import load_dotenv

from utils.compute_dataframe import load_csv_to_df

load_dotenv()

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
FORMATIONS_PATH = f"{RESULT_PATH}/{os.getenv("FORMATIONS_PATH")}"

def load_formations():
    """
    Récupère les informations des formations depuis le csv des résultats.

    Returns:
        dataframe : Dataframe pandas - Fichier formations.csv
    """
    dataframe = load_csv_to_df(FORMATIONS_PATH)
    return dataframe
