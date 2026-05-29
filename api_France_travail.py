import os
import requests
from dotenv import load_dotenv
import time

# Chargement des variables d'environnement (.env)
load_dotenv()

def get_france_travail_token():
    """
    Se connecte à l'authentification France Travail pour récupérer le Token d'accès.
    """
    # Nos identifiants importés depuis le .env
    client_id = os.getenv("ID_FRANCE_TRAVAIL")
    client_secret = os.getenv("CLE_FRANCE_TRAVAIL")
    
    donnees_authentification = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'api_offresdemploiv2 o2dsoffre'
    }

    url_token = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"

    reponse = requests.post(url_token, data=donnees_authentification, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    print("Code Statut HTTP Authentification :", reponse.status_code)
    print("Réponse brute de l'authentification :", reponse.text)
    
    resultat = reponse.json()   
    token = resultat.get("access_token")
    print("Token France Travail généré :", token)
    return token

def chercher_offres(token_access):
    """
    C'est cic que nous interrogeons l'API en utilisant notre Token d'accès (valide sinon erreur remonté)
    """
    url_recherche = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

    # Configuration des entêtes avec le Bearer token
    entetes = {
        'Authorization': f'Bearer {token_access}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    # Critères de recherche (Filtres)
    parametres = {
        'rome': 'H1402'
    }
    
    print("\nEnvoi de la requête de recherche à l'API...")
    reponse = requests.get(url_recherche, headers=entetes, params=parametres)
    print("Code statut du résultat de la recherche :", reponse.status_code)
    
    # Traitement des résultats si la requête réussit (200 ou 206 pour la pagination)
    if reponse.status_code in [200, 206]:
        donnees_brutes = reponse.json()
        liste_offres = donnees_brutes.get("resultats", [])

        print(f"Nombre d'offres trouvées : {len(liste_offres)}")
        print("-" * 50)

        for offre in liste_offres:
            ID_France_travail = offre.get("id")
            titre = offre.get("intitule")
            dateActualisation = offre.get("dateActualisation")
            code_rome = offre.get("romeCode")

            # Récupération de la région imbriquée
            lieu = offre.get("lieuTravail", {})
            Region = lieu.get("codeRegion")

            # Extraction et nettoyage de la liste des compétences
            competences_brutes = offre.get("competences", [])
            competences_propres = []
            
            for competence in competences_brutes:
                competences_propres.append({
                    "code": competence.get("code"),
                    "nom": competence.get("libelle")
                })
            
            # CORRECTION 2 : Ces prints sont sortis de la boucle "for competence"
            # Ils s'exécutent maintenant une seule fois par offre d'emploi.
            print(f"ID : {ID_France_travail}")
            print(f"Intitulé : {titre}")
            print(f"Date Actualisation : {dateActualisation}")
            print(f"Code ROME : {code_rome}")
            print(f"Code Région : {Region}")
            print(f"Compétences : {competences_propres}")
            print("-" * 50)
    else:
        print("Erreur lors de la recherche d'offres :", dict(reponse.headers))
        print(reponse.text)
    time.sleep(0.2)  # Pause pour éviter de surcharger l'API


# --- SCRIPT GLOBAL (POINT D'ENTRÉE) ---

# Appel a la Fonction qui stoque le token
token_access = get_france_travail_token()

# On vérifie que le token soit valide et on lance seulement si il est valide, sinon -> message d'erreur
if token_access:
    chercher_offres(token_access)
else:
    print("Impossible de lancer la recherche : Les identifiants du fichier .env ont été rejetés.")