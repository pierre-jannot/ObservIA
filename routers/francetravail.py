import os
import psycopg2
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "ObservIA")

def get_db_connection():

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@router.get("/offers-per-region")
def get_offers_per_region():
    """
    Route 1 : Nombre total d'offre par région.
    URL : GET /france-travail/offers-per-region
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT L.nom_region, COUNT(O.id_francetravail)
        FROM Offre_France_travail O
        JOIN Localisation L ON O.code_departement = L.code_Departement
        GROUP BY L.nom_region
        ORDER BY count DESC;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    result = [
        {"région": row[0], "nombre_offres_francetravail": int(row[1])}
        for row in rows
    ]
    return {"result": result}

@router.get("/offers-per-region/{region}")
def get_offers_per_specific_region(region: str):
    """
    Route 2 : Filrage pour 1 seul région (toujours toute les offres)
    URL : GET /france-travail/offers-per-region/Ile-de-France
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT L.nom_region, COUNT(O.id_francetravail)
        FROM Offre_France_travail O
        JOIN Localisation L ON O.code_departement = L.code_Departement
        WHERE L.nom_region = %s
        GROUP BY L.nom_region
        ORDER BY count DESC;
    """
    
    cursor.execute(query, (region,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = [
        {"région": row[0], "nombre_offres_francetravail": int(row[1])}
        for row in rows
    ]
    return {"result": result}

@router.get("/top-competences")
def get_top_competences():
    """
    Route 3 : Top 20 des compétences les plus demandées sur France Travail.
    Accessible via l'URL : GET /france-travail/top-competences
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT C.nom_competence, COUNT(OC.id_offre_competence)
        FROM Competence C
        JOIN Offre_Competence OC ON C.ID_Competence = OC.id_competence
        WHERE OC.id_francetravail IS NOT NULL
        GROUP BY C.nom_competence
        ORDER BY count DESC
        LIMIT 20;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = [
        {"compétence": row[0], "occurrences": int(row[1])}
        for row in rows
    ]
    return {"result": result}

