import os
import requests
import time
import psycopg2
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération des paramètres de configuration PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "ObservIA")  # Assure-toi que cette variable est bien définie sur ObservIA dans le .env

CONN_PARAMS = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME
}


def charger_codes_rome_depuis_bdd(conn):
    """Récupère uniquement les codes ROME présents en BDD qui commencent par M."""
    print("Récupération des codes ROME depuis la base de données...")
    cursor = conn.cursor()
    
    # Correction : On cible le premier élément du tableau postgres code_rome[1] 
    # et on filtre ceux qui commencent par 'M'
    query = "SELECT code_rome[1] FROM correspondance_rome_rncp WHERE code_rome[1] LIKE 'M%';"
    
    cursor.execute(query)
    liste_rome = [row[0] for row in cursor.fetchall() if row[0]]
    cursor.close()
    
    # Utilisation de set() pour éliminer les doublons éventuels
    return list(set(liste_rome))


def get_france_travail_token():
    """Récupère le token d'authentification OAuth2 auprès de France Travail."""
    client_id = os.getenv("ID_FRANCE_TRAVAIL")
    client_secret = os.getenv("CLE_FRANCE_TRAVAIL")

    reponse = requests.post(
        "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire",
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'api_offresdemploiv2 o2dsoffre'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if reponse.status_code != 200:
        print("Erreur d'obtention du token :", reponse.text)
        return None

    resultat = reponse.json()
    token = resultat.get("access_token")
    print(f"Token généré (expire dans {resultat.get('expires_in')}s)")
    return token


def stocker_offre_et_competences(cursor, offre):
    """Insère une offre, ses compétences et met à jour la table pivot."""
    
    # Extraction et nettoyage strict du code département (ex: 75, 13, 974)
    lieu = offre.get("lieuTravail", {})
    code_postal = lieu.get("codePostal")
    code_dept = None

    if code_postal and isinstance(code_postal, str):
        code_postal = code_postal.strip()
        if code_postal.startswith(("97", "98")):
            # Outre-mer : le département est sur 3 chiffres (ex: 97400 -> 974)
            code_dept = code_postal[:3]
        else:
            # Métropole : le département est sur 2 chiffres (ex: 75001 -> 75)
            code_dept = code_postal[:2]
            
    # Sécurité pour respecter la contrainte de taille de la colonne en BDD
    if code_dept:
        code_dept = code_dept[:5]

    # Insertion sécurisée contre les doublons d'offres (ON CONFLICT)
    insert_offre_query = """
    INSERT INTO Offre_France_travail (ID_FranceTravail, code_rome, code_Region, Competence, dateActualisation, dateCreation)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (ID_FranceTravail) DO UPDATE 
    SET dateActualisation = EXCLUDED.dateActualisation
    RETURNING ID_FranceTravail;
    """
    
    id_offre_brut = offre.get('id')
    rome_code_param = offre.get('romeCode') 

    cursor.execute(insert_offre_query, (
        id_offre_brut,
        rome_code_param,
        code_dept,
        offre.get('intitule'),
        offre.get('dateActualisation'),
        offre.get('dateCreation')
    ))
    
    res = cursor.fetchone()
    if not res:
        # L'offre existait déjà et n'a pas été modifiée/insérée à nouveau
        return 
    id_france_travail = res[0]

    # Insertion des compétences liées et alimentation de la table pivot
    liste_competences = offre.get("competences", [])
    for comp in liste_competences:
        nom_comp = comp.get("libelle")
        if not nom_comp:
            continue
            
        insert_comp_query = """
        INSERT INTO Competence (nom_competence)
        VALUES (%s)
        ON CONFLICT (nom_competence) DO NOTHING;
        """
        cursor.execute(insert_comp_query, (nom_comp,))
        
        select_comp_query = "SELECT ID_Competence FROM Competence WHERE nom_competence = %s;"
        cursor.execute(select_comp_query, (nom_comp,))
        id_competence = cursor.fetchone()[0]

        # FIX OBLIGATOIRE PK : Insertion de 0 au lieu de NULL pour la clé composite
        insert_pivot_query = """
        INSERT INTO Offre_Competence (ID_Competence, ID_FranceTravail, ID_Scraping)
        VALUES (%s, %s, 0)
        ON CONFLICT DO NOTHING;
        """
        cursor.execute(insert_pivot_query, (id_competence, id_france_travail))


def chercher_offres(token_access, code_rome, conn):
    """Parcourt l'API de France Travail pour un code ROME donné et stocke les résultats."""
    cursor = conn.cursor()
    entetes = {
        'Authorization': f'Bearer {token_access}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    debut = 0          
    taille = 149       
    total = None       

    while True:
        params = {
            'codeROME': code_rome,
            'range': f"{debut}-{debut + taille}"
        }

        reponse = requests.get(
            "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
            headers=entetes,
            params=params
        )

        # Gestion du Rate Limit de l'API
        if reponse.status_code == 429:
            print("  Rate limit atteint, pause 15s...")
            time.sleep(15)
            continue 

        # Pas de contenu (0 offre pour ce code)
        if reponse.status_code == 204:
            if debut == 0:
                print(f"  [{code_rome}] 0 offre au total (aucun poste vacant)")
            break

        if reponse.status_code not in [200, 206]:
            print(f"  Erreur {reponse.status_code} sur {code_rome} : {reponse.text}")
            break

        # Extraction de la taille totale du lot d'offres disponible
        if total is None:
            content_range = reponse.headers.get("Content-Range", "")
            if "/" in content_range:
                total_str = content_range.split("/")[-1]
                total = int(total_str) if total_str.isdigit() else 3000
                print(f"  [{code_rome}] {total} offres trouvées")
            else:
                total = 3000

        data = reponse.json()
        liste_offres = data.get("resultats", [])

        try:
            for offre in liste_offres:
                stocker_offre_et_competences(cursor, offre)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Erreur d'insertion pour le lot {code_rome} : {e}")
            break

        # Si on récupère moins d'offres que la taille demandée, on a fini
        if len(liste_offres) < (taille + 1):
            break

        debut += taille + 1

        # Limite maximale de pagination autorisée par l'API France Travail
        if debut >= total or debut >= 3000:
            break

        # Temporisation pour respecter les quotas d'appels par seconde de l'API
        time.sleep(0.5)
        
    cursor.close()


if __name__ == "__main__":
    token_access = get_france_travail_token()

    if token_access:
        try:
            print("Connexion à la base de données...")
            conn = psycopg2.connect(**CONN_PARAMS)
            
            CODES_ROME = charger_codes_rome_depuis_bdd(conn)
            print(f"{len(CODES_ROME)} codes ROME uniques trouvés en BDD.\n")
            
            # Application de la contrainte unique de sécurité sur la table Competence
            with conn.cursor() as cur:
                cur.execute("""
                    ALTER TABLE Competence 
                    DROP CONSTRAINT IF EXISTS unique_nom_competence;
                    ALTER TABLE Competence 
                    ADD CONSTRAINT unique_nom_competence UNIQUE (nom_competence);
                """)
                conn.commit()

            # Lancement de la collecte pour chaque code ROME trouvé
            for code in CODES_ROME:
                chercher_offres(token_access, code, conn)
                
            conn.close()
            print("\nTraitement et stockage en base de données terminés avec succès.")
        except Exception as e:
            print(f"Erreur générale pendant l'exécution : {e}")
    else:
        print("Impossible de démarrer le script : Token invalide.")