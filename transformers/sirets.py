import pandas as pd

from tqdm import tqdm

from extractors.sirets import get_region_from_siret

COLONNES_MAPPING = {
    "siret":                    "id_siret",
    "nom_raison_sociale":       "name",
    "location":                 "id_region",
}

COLONNES_DB = list(COLONNES_MAPPING.values())

def prepare_siret_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme et sélectionne les colonnes du DataFrame siret
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

def get_sirets_information(unique_sirets):
    print('\nAvancement récupération informations SIRET :\n')
    pbar = tqdm(total=len(unique_sirets))
    siret_info_list = []
    for siret in unique_sirets:
        siret_information = get_region_from_siret(siret)
        siret_info_list.append(siret_information)
        pbar.update(1)
    return siret_info_list
