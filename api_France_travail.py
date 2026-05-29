import os          # pour lire les variables d'environnement (.env)
import requests    # pour faire des appels HTTP à l'API
from dotenv import load_dotenv  # pour charger le fichier .env
import time        # pour les pauses entre appels API

load_dotenv()  # lit ton fichier .env et charge ID_FRANCE_TRAVAIL et CLE_FRANCE_TRAVAIL
               # dans l'environnement, sinon os.getenv() retournerait None

# Liste simple des codes ROME tech — une liste suffit, pas besoin d'un dictionnaire
# car on ne veut pas afficher l'intitulé du ROME, juste faire les appels
CODES_ROME_TECH = [
    'M1801', 'M1802', 'M1803', 'M1804', 'M1805',
    'M1806', 'M1807', 'M1808', 'M1810',
    'I1401', 'I1305', 'I1307', 'I1302',
    'H1202', 'H1206', 'H1208', 'H1209', 'H1210',
    'E1101', 'E1104', 'E1205'
]


def get_france_travail_token():
    # os.getenv() va chercher la valeur dans le .env chargé par load_dotenv()
    client_id     = os.getenv("ID_FRANCE_TRAVAIL")
    client_secret = os.getenv("CLE_FRANCE_TRAVAIL")

    reponse = requests.post(
        "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire",
        data={
            'grant_type':    'client_credentials',  # type d'auth machine-to-machine (pas d'utilisateur humain)
            'client_id':     client_id,
            'client_secret': client_secret,
            'scope':         'api_offresdemploiv2 o2dsoffre'
            
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    resultat = reponse.json()  # convertit la réponse texte en dictionnaire Python
    token = resultat.get("access_token")  # extrait uniquement le token du dictionnaire
    print(f"Token généré (expire dans {resultat.get('expires_in')}s)")
    return token  # on retourne le token pour l'utiliser dans chercher_offres()


def chercher_offres(token_access, code_rome):
    entetes = {
        'Authorization': f'Bearer {token_access}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    reponse = requests.get(
        "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
        headers=entetes,
        params={'rome': code_rome}
    )

    if reponse.status_code == 429:
        print(f"  Rate limit atteint, pause 15s...")
        time.sleep(15)
        return chercher_offres(token_access, code_rome)  # rappel récursif de la même fonction

    if reponse.status_code not in [200, 206]:
        
        print(f"  Erreur {reponse.status_code} sur {code_rome}")
        return

    liste_offres = reponse.json().get("resultats", [])
    # .get("resultats", []) : si la clé "resultats" n'existe pas, retourne [] 
    # plutôt que de planter avec une KeyError
    print(f"  [{code_rome}] {len(liste_offres)} offres trouvées")
    print("-" * 50)

    for offre in liste_offres:
        lieu = offre.get("lieuTravail", {})
        # lieuTravail est un sous-dictionnaire imbriqué dans l'offre
        # on le sort d'abord dans une variable pour ne pas répéter offre.get("lieuTravail")

        localisation = f"{lieu.get('libelle', '')} ({lieu.get('codePostal', '')})"


        competences = [
            {"code": c.get("code"), "nom": c.get("libelle")}
            for c in offre.get("competences", [])

        ]

        print(f"ID : {offre.get('id')}")
        print(f"Intitulé : {offre.get('intitule')}")
        print(f"Date Actualisation : {offre.get('dateActualisation')}")
        print(f"Code ROME : {offre.get('romeCode')}")
        print(f"Localisation : {localisation}")
        print(f"Compétences : {competences}")
        print("-" * 50)

    time.sleep(0.3)
    # pause de 300ms entre chaque code ROME
    # évite de surcharger l'API et de déclencher le rate limit (429)


# ── POINT D'ENTRÉE ──────────────────────────────────────────────────

token_access = get_france_travail_token()

if token_access:
    for code in CODES_ROME_TECH:
        # on boucle sur chaque code ROME tech et on appelle chercher_offres()
        # le token est le même pour tous les appels (valide 25 min)
        chercher_offres(token_access, code)
else:
    print("Token invalide.")