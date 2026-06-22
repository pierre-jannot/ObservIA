import os
import requests
import csv
import time
from dotenv import load_dotenv

load_dotenv()


def charger_codes_rome(chemin_csv):
    liste_rome = []
    with open(chemin_csv, "r", encoding="utf-8-sig") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=";")
        for ligne in lecteur:
            if ligne["code_rome"] not in liste_rome:
                liste_rome.append(ligne["code_rome"])
    return liste_rome


def get_france_travail_token():
    client_id     = os.getenv("ID_FRANCE_TRAVAIL")
    client_secret = os.getenv("CLE_FRANCE_TRAVAIL")

    reponse = requests.post(
        "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire",
        data={
            'grant_type':    'client_credentials',
            'client_id':     client_id,
            'client_secret': client_secret,
            'scope':         'api_offresdemploiv2 o2dsoffre'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if reponse.status_code != 200:
        print("Erreur de token :", reponse.text)
        return None

    resultat = reponse.json()
    token = resultat.get("access_token")
    print(f"Token généré (expire dans {resultat.get('expires_in')}s)")
    return token


def chercher_offres(token_access, code_rome, writer):
    entetes = {
        'Authorization': f'Bearer {token_access}',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    debut = 0          
    taille = 149       
    total = None       

    while True:
        # CORRECTION 1 : Le paramètre s'appelle 'codeROME'
        params = {
            'codeROME': code_rome,
            'range': f"{debut}-{debut + taille}"
        }

        reponse = requests.get(
            "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search",
            headers=entetes,
            params=params
        )

        if reponse.status_code == 429:
            print("  Rate limit atteint, pause 15s...")
            time.sleep(15)
            continue 

        # CORRECTION 2 : L'API renvoie 204 quand elle ne trouve aucune offre pour ce code
        if reponse.status_code == 204:
            if debut == 0:
                print(f"  [{code_rome}] 0 offre au total (aucun poste vacant actuellement)")
            break

        if reponse.status_code not in [200, 206]:
            print(f"  Erreur {reponse.status_code} sur {code_rome} : {reponse.text}")
            break

        # CORRECTION 3 : Récupérer le nombre total via les headers ("Content-Range: offres 0-149/1500")
        if total is None:
            content_range = reponse.headers.get("Content-Range", "")
            if "/" in content_range:
                total_str = content_range.split("/")[-1]
                total = int(total_str) if total_str.isdigit() else 3000
                print(f"  [{code_rome}] {total} offres au total")
            else:
                total = 3000

        data = reponse.json()
        liste_offres = data.get("resultats", [])

        for offre in liste_offres:
            lieu = offre.get("lieuTravail", {})
            localisation = f"{lieu.get('libelle', '')} ({lieu.get('codePostal', '')})"

            competences = [
                {"code": c.get("code"), "nom": c.get("libelle")}
                for c in offre.get("competences", [])
            ]

            writer.writerow([
                offre.get('id'),
                offre.get('intitule'),
                offre.get('dateActualisation'),
                offre.get('romeCode'),
                localisation,
                competences
            ])

        # CORRECTION 4 : Arrêter proprement quand on atteint la fin des offres
        if len(liste_offres) < (taille + 1):
            break

        debut += taille + 1

        if debut >= total or debut >= 3000:
            break

        time.sleep(0.3)


# ── POINT D'ENTRÉE ──────────────────────────────────────────────────
if __name__ == "__main__":
    CODES_ROME = charger_codes_rome("correspondance-rome-rncp.csv")
    print(f"{len(CODES_ROME)} codes ROME chargés depuis le CSV\n")

    token_access = get_france_travail_token()

    if token_access:
        with open("offres.csv", "w", encoding="utf-8-sig", newline="") as fichier:
            writer = csv.writer(fichier, delimiter=";")
            writer.writerow(["id", "intitule", "dateActualisation", "romeCode", "localisation", "competences"])

            for code in CODES_ROME:
                chercher_offres(token_access, code, writer)
                
        print("\nTraitement terminé. Résultats sauvegardés dans offres.csv")
    else:
        print("Token invalide.")