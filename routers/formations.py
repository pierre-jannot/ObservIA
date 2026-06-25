from fastapi import APIRouter, Query
from utils.compute_dataframe import get_quarter_values, sum_values, get_filtered_values, load_csv_to_df
from extractors.formations import load_formations
from extractors.sirets import load_sirets

router = APIRouter()

@router.get("/entry-per-quarter")
def get_formation_entry_per_quarter(
    zone: list[str] | None = Query(None)
):
    dataframe = load_formations()
    if zone:
        sirets = load_sirets()
        correspondance = dict(zip(sirets["siret"], sirets["departement"]))
        dataframe["zone"] = dataframe["siret_of_contractant"].map(correspondance)
        dataframe = get_filtered_values(dataframe, "zone", zone)
    dataframe = get_quarter_values(dataframe, "annee_mois")
    dataframe = sum_values(dataframe, "entrees_formation", "quarter")
    result = [
    {"trimestre": str(index), "nombre_entrées_formations": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}

@router.get("/exit-per-quarter")
def get_formation_exit_per_quarter(
    zone: list[str] | None = Query(None)
):
    dataframe = load_formations()
    if zone:
        sirets = load_sirets()
        correspondance = dict(zip(sirets["siret"], sirets["departement"]))
        dataframe["zone"] = dataframe["siret_of_contractant"].map(correspondance)
        dataframe = get_filtered_values(dataframe, "zone", zone)
    dataframe = get_quarter_values(dataframe, "annee_mois")
    dataframe = sum_values(dataframe, "sorties_realisation_totale", "quarter")
    result = [
    {"trimestre": str(index), "nombre_sorties_formations": int(value)}
    for index, value in dataframe.items()
    ]
    return {"result": result}