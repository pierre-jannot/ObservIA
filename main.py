from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.compute_dataframe import get_filtered_values, get_quarter_values, get_unique_values, count_unique_values, sum_values
from compute_freework_offers import compute_freework_offers
from compute_formations import compute_all

import pandas as pd

compute_all()
compute_freework_offers()

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
    dataframe = sum_values(dataframe, "entrees_formation", "quarter")
    result = [
    {"trimestre": str(index), "nombre_entrées_formations": int(value)}
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

@app.get("/offers-per-department")
def get_formations_per_department():
    dataframe = pd.read_csv("result/freework_offers.csv", sep=";", encoding="utf-8")
    departments = pd.read_csv("result/departments.csv", sep=";", encoding="utf-8")
    dataframe = get_filtered_values(dataframe, "location", departments["nom_departement"])
    dataframe = count_unique_values(dataframe, "location")
    result = [
    {"département": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}

@app.get("/offers-per-region")
def get_formations_per_region():
    dataframe = pd.read_csv("result/freework_offers.csv", sep=";", encoding="utf-8")
    departments = pd.read_csv("result/departments.csv", sep=";", encoding="utf-8")
    correspondance = dict(zip(departments["nom_departement"], departments["nom_region"]))
    dataframe["region"] = dataframe["location"].map(correspondance).fillna(dataframe["location"])
    dataframe = count_unique_values(dataframe, "region")
    result = [
    {"région": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}


@app.get("/offers-per-region/{region}")
def get_formations_per_region(region: str):
    dataframe = pd.read_csv("result/freework_offers.csv", sep=";", encoding="utf-8")
    departments = pd.read_csv("result/departments.csv", sep=";", encoding="utf-8")
    correspondance = dict(zip(departments["nom_departement"], departments["nom_region"]))
    dataframe["region"] = dataframe["location"].map(correspondance).fillna(dataframe["location"])
    dataframe = get_filtered_values(dataframe, "region", [region])
    dataframe = count_unique_values(dataframe, "region")
    result = [
    {"région": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}