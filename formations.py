import pandas as pd

def init_data():
    formations = pd.read_csv("data/datagouv/entree_sortie_formation.csv", sep=";", encoding="utf-8")
    correspondances = pd.read_csv("data/datagouv/table-correspondance-rome-rncp.csv", sep=";", encoding="utf-8")

    return formations, correspondances

def filter_data(formations, correspondances):
    formations = formations.drop(columns=["annee", "mois", "type_referentiel", "code_rs", "code_certifinfo", "siret_of_contractant", "raison_sociale_of_contractant", "sorties_realisation_partielle", "sorties_realisation_totale", "date_chargement"])
    formations = formations[formations["code_rncp"] != -1]
    formations = formations[formations["entrees_formation"] > 0]

    correspondances["code_rncp"] = correspondances["code_rncp"].str.extract(r"(\d+)")[0].astype(int)

    data = correspondances.merge(formations, on="code_rncp", how="inner")

    return data

def write_data(data):
    data.to_csv("result/formations.csv", sep=";", index=False, encoding="utf-8")