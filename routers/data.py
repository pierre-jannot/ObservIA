"""
Routes d'initialisation des données.
"""

from fastapi import APIRouter

from pipeline.compute_freework_offers import compute_freework_offers
from pipeline.compute_formations import compute_all

router = APIRouter()

@router.post("/init")
def init():
    """
    Scraping et traitement de toutes les données brutes puis écriture en csv.

    Args:
        Pas d'arguments

    Returns:
        json - result : résultat de l'opération
    """
    compute_all()
    return {"result": "Initialisation effectuée avec succès."}

@router.post("/get-freework-offers")
def get_freework_offers():
    compute_freework_offers()
    return {"result": "Offres freework récupérées."}
