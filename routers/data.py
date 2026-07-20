from fastapi import APIRouter

from pipeline.compute_freework_offers import compute_freework_offers
from pipeline.compute_formations import compute_all

router = APIRouter()

@router.post("/init")
def init():
    compute_all()
    compute_freework_offers()
    return {"result": "Initialisation effectuée avec succès."}
