"""
Fonctions utilitaires pour les indicateurs de formations.
"""

from utils.compute_dataframe import get_quarter_values, sum_values

def column_per_quarter(dataframe, column):
    """
    Retourne la quantité par trimestre des valeurs uniques de la colonne choisie.

    Args:
        dataframe : Dataframe pandas
        column : str - Nom de la colonne visée par l'indicateur

    Returns:
        result : dict - Quantité par trimestre des valeurs uniques de la colonne choisie
    """
    dataframe = get_quarter_values(dataframe, "annee_mois")
    dataframe = sum_values(dataframe, column, "quarter")
    result = [
        {"trimestre": str(index), f"nombre_{column}": int(value)}
        for index, value in dataframe.items()
    ]
    return result
