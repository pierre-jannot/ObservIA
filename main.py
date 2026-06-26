from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import formations, freework, data

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

@app.get("/")
def root():
    return {"status": "ok"}