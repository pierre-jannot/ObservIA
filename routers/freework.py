from fastapi import APIRouter, Query

from utils.compute_dataframe import get_filtered_values, get_quarter_values, count_unique_values
from extractors.offers import load_freework_offers
from extractors.departments import load_departments

router = APIRouter()

@router.get("/all")
def get_all(limit: int = Query(50, le=500, description="Nombre max de résultats")):
    dataframe = load_freework_offers()
    dataframe = dataframe.fillna("")
    dataframe = dataframe.head(limit)
    return {"result": dataframe.to_dict(orient="records")}

@router.get("/offers-per-quarter")
def get_offers_per_quarter(
    zone: list[str] | None = Query(None)
):
    dataframe = load_freework_offers()
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
    dataframe = load_freework_offers()
    departments = load_departments()
    dataframe = get_filtered_values(dataframe, "location", departments["nom_departement"])
    dataframe = count_unique_values(dataframe, "location")
    result = [
    {"département": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}

@router.get("/offers-per-region")
def get_offers_per_region():
    dataframe = load_freework_offers()
    departments = load_departments()
    correspondance = dict(zip(departments["nom_departement"], departments["nom_region"]))
    dataframe["region"] = dataframe["location"].map(correspondance).fillna(dataframe["location"])
    dataframe = count_unique_values(dataframe, "region")
    result = [
    {"région": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}


@router.get("/offers-per-region/{region}")
def get_offers_per_chosen_region(region: str):
    dataframe = load_freework_offers()
    departments = load_departments()
    correspondance = dict(zip(departments["nom_departement"], departments["nom_region"]))
    dataframe["region"] = dataframe["location"].map(correspondance).fillna(dataframe["location"])
    dataframe = get_filtered_values(dataframe, "region", [region])
    dataframe = count_unique_values(dataframe, "region")
    result = [
    {"région": index, "nombre_offres_freework": int(value)}
    for index, value in dataframe.sort_values(ascending=False).items()
    ]
    return {"result": result}
