import pandas as pd

COLONNES_MAPPING = {
    "code_rome":            "code_rome",
    "code_rncp":            "code_rncp",
}

COLONNES_DB = list(COLONNES_MAPPING.values())

def prepare_rome_rncp_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme et sélectionne les colonnes du DataFrame rome rncp
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