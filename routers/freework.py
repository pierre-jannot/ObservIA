from utils.compute_dataframe import get_filtered_values, get_quarter_values, count_unique_values
from fastapi import APIRouter, Query

import pandas as pd

router = APIRouter()

@router.get("/offers-per-quarter")
def get_offers_per_quarter(
    zone: list[str] | None = Query(None)
):
    dataframe = pd.read_csv("result/freework_offers.csv", sep=";", encoding="utf-8")
    if zone:
        dataframe = get_filtered_values(dataframe, "location", zone)
    dataframe = get_quarter_values(dataframe, "publication_date")
    dataframe = count_unique_values(dataframe, "quarter")
    result = [
    {"trimestre": str(index), "nombre_offres_freework": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}

@router.get("/offers-per-department")
def get_offers_per_department():
    dataframe = pd.read_csv("result/freework_offers.csv", sep=";", encoding="utf-8")
    departments = pd.read_csv("result/departments.csv", sep=";", encoding="utf-8")
    dataframe = get_filtered_values(dataframe, "location", departments["nom_departement"])
    dataframe = count_unique_values(dataframe, "location")
    result = [
    {"département": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}

@router.get("/offers-per-region")
def get_offers_per_region():
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


@router.get("/offers-per-region/{region}")
def get_offers_per_region(region: str):
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