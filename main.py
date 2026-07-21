from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from compute_freework_offers import compute_freework_offers
from compute_formations import compute_all
from routers import formations, freework, francetravail, data

compute_all()
compute_freework_offers()

app = FastAPI(
    title="Tensions formations et offres d'emploi Tech IA",
    description="API d'indicateurs de tension recrutement Tech/IA",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router, prefix="/data", tags=["Données"])
app.include_router(formations.router, prefix="/formations", tags=["Formations"])
app.include_router(freework.router, prefix="/freework", tags=["Freework"])
app.include_router(francetravail.router, prefix="/france-travail", tags=["France Travail"])

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return RedirectResponse(url="http://localhost:8000/docs")