import pandas as pd
from extractors.sirets import load_sirets

COLONNES_MAPPING = {
    "siret_of_contractant":         "id_siret",
    "intitule_certification":       "title",
    "entrees_formation":            "entries",
    "sorties_realisation_totale":   "exits_full",
    "annee_mois":                   "year_month",
    "code_rncp":                    "code_rncp",
}

COLONNES_DB = list(COLONNES_MAPPING.values())

def prepare_formation_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme et sélectionne les colonnes du DataFrame formations
    pour correspondre au schéma de la table PostgreSQL.

    Args:
        df: DataFrame brut issu du CSV MonCompteFormation.

    Returns:
        DataFrame prêt pour l'insertion en base.
    """
    df = df.rename(columns=COLONNES_MAPPING)
    df = df[COLONNES_DB]
    df = df.where(pd.notna(df), None)
    return df

def filter_data(formations, correspondances):
    formations = formations.drop(columns=["annee", "mois", "type_referentiel",
                                          "code_rs", "code_certifinfo",
                                          "raison_sociale_of_contractant",
                                          "sorties_realisation_partielle", "date_chargement"])
    formations = formations[formations["code_rncp"] != -1]
    formations = formations[formations["entrees_formation"] > 0]

    correspondances = correspondances[correspondances["code_rome"].str.contains("M", na=False)]

    correspondances = correspondances.drop(columns=["niveau_rncp", "intitule_rncp"])
    correspondances["code_rncp"] = correspondances["code_rncp"].str.extract(r"(\d+)")[0].astype(int)

    formations = formations[formations["code_rncp"].isin(correspondances["code_rncp"])]
    correspondances = correspondances[correspondances["code_rncp"].isin(formations["code_rncp"])]

    return formations, correspondances

def add_zone_column(dataframe):
    sirets = load_sirets()
    correspondance = dict(zip(sirets["siret"], sirets["location"]))
    dataframe["zone"] = dataframe["siret_of_contractant"].map(correspondance)
    return dataframe