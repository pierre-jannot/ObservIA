import pandas as pd
import os

def load_csv_data():
    formations = pd.read_csv("data/datagouv/entree_sortie_formation.csv", sep=";", encoding="utf-8")
    correspondances = pd.read_csv("data/datagouv/table-correspondance-rome-rncp.csv", sep=";", encoding="utf-8")

    return formations, correspondances