import os
import token
import requests
from dotenv import load_dotenv

load_dotenv()

def get_france_travail_token():
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"


    # nos identifiants (auth) importé depuis le .env
    client_id = os.getenv("ID_FRANCE_TRAVAIL")
    client_secret = os.getenv("CLE_FRANCE_TRAVAIL")
    donnees_authentification = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'api_offresdemploiv2'
    }

    url_token = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"

    reponse = requests.post(url_token, data=donnees_authentification)
    print("Code Statut HTTP :", reponse.status_code)
    print("Réponse brute de l'API :", reponse.text)
    resultat = reponse.json()   
    token = resultat.get("access_token")
    print("Token France Travail:",token)
    return token

def chercher_offres(token_access):
    #entete permettant d'accéder à l'API avec le token
    entetes = {
        'Authorization': f'Bearer {token_access}',
    }

    parametres = {
        'rome': 'N1101'
    }

    print("Entêtes de la requête :", entetes)
    print("Paramètres de la requête :", parametres)
    
get_france_travail_token()
token_access = get_france_travail_token()
chercher_offres(token_access)
