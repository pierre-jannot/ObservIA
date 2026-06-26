from compute_freework_offers import compute_freework_offers
from compute_formations import compute_all

from fastapi import APIRouter

router = APIRouter()

@router.post("/init")
def init():
    compute_all()
    compute_freework_offers()
    return({"result": "Initialisation effectuée avec succès."})