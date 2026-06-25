import os

from utils.compute_dataframe import load_csv_to_df
from dotenv import load_dotenv

load_dotenv()

RESULT_PATH = os.getenv("RESULT_FOLDER_PATH")
FORMATIONS_PATH = f"{RESULT_PATH}/{os.getenv("FORMATIONS_PATH")}"

def load_formations():
    dataframe = load_csv_to_df(FORMATIONS_PATH)
    return dataframe