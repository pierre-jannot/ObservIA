import pandas as pd

COLONNES_MAPPING_FREEWORK = {
    "id":                       "id_offer",
    "title":                    "title",
    "profile":                  "description",
    "experience":               "experience",
    "min_daily_salary":         "min_daily_sal",
    "max_daily_salary":         "max_daily_sal",
    "min_annual_salary":        "min_annual_sal",
    "max_annual_salary":        "max_annual_sal",
    "month_duration":           "month_dur",
    "location":                 "id_region",
    "publication_date":         "pub_date",
}

COLONNES_MAPPING_FRANCE_TRAVAIL = {
    "id_francetravail":         "id_offer",
    "title":                    "title",
    "profile":                  "description",
    "experience":               "experience",
    "min_daily_salary":         "min_daily_sal",
    "max_daily_salary":         "max_daily_sal",
    "min_annual_salary":        "min_annual_sal",
    "max_annual_salary":        "max_annual_sal",
    "month_duration":           "month_dur",
    "location":                 "id_region",
    "publication_date":         "pub_date",
    "rome_code":                "rome_code",
}

COLONNES_DB_FREEWORK = list(COLONNES_MAPPING_FREEWORK.values())

COLONNES_DB_FRANCE_TRAVAIL = list(COLONNES_MAPPING_FRANCE_TRAVAIL.values())

def prepare_freework_offer_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme et sélectionne les colonnes du DataFrame siret
    pour correspondre au schéma de la table PostgreSQL.

    Args:
        df: DataFrame brut issu du CSV MonCompteFormation.

    Returns:
        DataFrame prêt pour l'insertion en base.
    """
    df = df.rename(columns=COLONNES_MAPPING_FREEWORK)
    df = df[COLONNES_DB_FREEWORK]
    df["source"] = "Freework"
    df = df.where(pd.notna(df), None)
    return df

def prepare_france_travail_offer_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomme et sélectionne les colonnes du DataFrame siret
    pour correspondre au schéma de la table PostgreSQL.

    Args:
        df: DataFrame brut issu du CSV MonCompteFormation.

    Returns:
        DataFrame prêt pour l'insertion en base.
    """
    df = df.rename(columns=COLONNES_MAPPING_FRANCE_TRAVAIL)
    df = df[COLONNES_DB_FRANCE_TRAVAIL]
    df["source"] = "France Travail"
    df = df.where(pd.notna(df), None)
    return df