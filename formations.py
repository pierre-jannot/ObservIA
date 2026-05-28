import pandas as pd
import os

def init_data():
    formations = pd.read_csv("data/datagouv/entree_sortie_formation.csv", sep=";", encoding="utf-8")
    correspondances = pd.read_csv("data/datagouv/table-correspondance-rome-rncp.csv", sep=";", encoding="utf-8")

    return formations, correspondances

def filter_data(formations, correspondances):
    formations = formations.drop(columns=["annee", "mois", "type_referentiel", "code_rs", "code_certifinfo", "siret_of_contractant", "raison_sociale_of_contractant", "sorties_realisation_partielle", "sorties_realisation_totale", "date_chargement"])
    formations = formations[formations["code_rncp"] != -1]
    formations = formations[formations["entrees_formation"] > 0]

    correspondances["code_rncp"] = correspondances["code_rncp"].str.extract(r"(\d+)")[0].astype(int)

    formations = formations[formations["code_rncp"].isin(correspondances["code_rncp"])]
    correspondances = correspondances[correspondances["code_rncp"].isin(formations["code_rncp"])]

    return formations, correspondances

def write_data(formations, correspondances):
    if os.path.exists("result/formations.csv"):
        print("Données result/formations.csv existantes. Réécriture des données ignorée.")
    else:
        formations.to_csv("result/formations.csv", sep=";", index=False, encoding="utf-8")
        print("Données result/formations.csv écrites avec succès.")

    if os.path.exists("result/correspondances.csv"):
        print("Données result/correspondances.csv existantes. Réécriture des données ignorée.")
    else:
        correspondances.to_csv("result/correspondances.csv", sep=";", index=False, encoding="utf-8")
        print("Données result/correspondances.csv écrites avec succès.")

def compute_formation_data():
    if os.path.exists("result/formations.csv") and os.path.exists("result/correspondances.csv"):
        print("Données result/formations.csv et correspondances.csv existantes. Réécriture des données ignorée.")
        return
    else:
        formations, correspondances = init_data()
        formations, correspondances = filter_data(formations=formations, correspondances=correspondances)
        write_data(formations, correspondances)