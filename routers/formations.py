from fastapi import APIRouter
from utils.compute_dataframe import get_quarter_values, sum_values

import pandas as pd

router = APIRouter()

@router.get("/entry-per-quarter")
def get_formation_entry_per_quarter():
    dataframe = pd.read_csv("result/formations.csv", sep=";", encoding="utf-8")
    dataframe = get_quarter_values(dataframe, "annee_mois")
    dataframe = sum_values(dataframe, "entrees_formation", "quarter")
    result = [
    {"trimestre": str(index), "nombre_entrées_formations": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}

@router.get("/exit-per-quarter")
def get_formation_exit_per_quarter():
    dataframe = pd.read_csv("result/formations.csv", sep=";", encoding="utf-8")
    dataframe = get_quarter_values(dataframe, "annee_mois")
    dataframe = sum_values(dataframe, "sorties_realisation_totale", "quarter")
    result = [
    {"trimestre": str(index), "nombre_sorties_formations": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}