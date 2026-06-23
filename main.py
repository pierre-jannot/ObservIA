from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.compute_dataframe import get_filtered_values, get_quarter_values, get_unique_values, count_unique_values

import pandas as pd

app = FastAPI(
    title="Tensions formations et offres d'emploi Tech IA",
    description="API d'indicateurs de tension recrutement Tech/IA",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/formations-per-quarter")
def get_offers_per_quarter():
    dataframe = pd.read_csv("result/formations.csv", sep=";", encoding="utf-8")
    dataframe = get_quarter_values(dataframe, "annee_mois")
    dataframe = count_unique_values(dataframe, "quarter")
    result = [
    {"trimestre": str(index), "nombre_formations": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}

@app.get("/offers-per-quarter")
def get_offers_per_quarter():
    dataframe = pd.read_csv("result/freework_offers.csv", sep=";", encoding="utf-8")
    dataframe = get_quarter_values(dataframe, "publication_date")
    dataframe = count_unique_values(dataframe, "quarter")
    result = [
    {"trimestre": str(index), "nombre_offres_freework": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}