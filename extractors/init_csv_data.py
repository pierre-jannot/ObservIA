import os

from dotenv import load_dotenv

from utils.compute_dataframe import load_csv_to_df

load_dotenv()

SOURCES_PATH = os.getenv("SOURCES_FOLDER_PATH")
E_S_FORMATIONS_PATH = f"{SOURCES_PATH}/{os.getenv("E_S_FORMATIONS_PATH")}"
CORRESPONDANCES_PATH = f"{SOURCES_PATH}/{os.getenv("TABLE_CORRESP_PATH")}"

def load_init_data():
    formations = load_csv_to_df(E_S_FORMATIONS_PATH)
    correspondances = load_csv_to_df(CORRESPONDANCES_PATH)

    return formations, correspondances
