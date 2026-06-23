from compute_formations import compute_formation_data, compute_sirets_information, compute_departments_information
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def root():
    return {"status": "ok"}

def main():
    compute_formation_data()
    compute_departments_information()
    compute_sirets_information()
    return

if __name__ == "__main__":
    main()