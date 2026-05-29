import requests # télécharge la page web 
from bs4 import BeautifulSoup # permet de lire et fouiller le HTML de la page 
import re # cherche patterns dans le texte (trouver une date etc)
import time           # faire des pauses
import random         # générer des nombres aléatoires
import json           # sauvegarder en fichier JSON

HEADERS = {"User-Agent": "Mozilla/5.0"} #  On se déguise en vrai navigateur pour ne pas se faire bloquer
BASE_URL = "https://www.free-work.com" # L'adresse de base du site, réutilisée partout dans le code

def scrape_freework_offer(url):
    try:
        soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser") # télécharge la page de l'offre

        # Juste après soup = BeautifulSoup(...)
        #print(soup.prettify()[:3000])  # affiche les 3000 premiers caractères du HTML brut

         # Titre
        titre = soup.find("h1").get_text(strip=True) # Va chercher le titre depuis la balise <h1> dans le HTML de la page et extrait le texte brut -  Résultat brut : "Offre d'emploiLead Architect"
        titre = titre.replace("Offre d'emploi", "").replace("Mission freelance", "").strip()  
        # .replace("Offre d'emploi", "") → remplace "Offre d'emploi" par rien (= supprime)
        # .replace("Mission freelance", "") → même chose pour "Mission freelance"
        # .strip() → supprime les espaces qui traînent au début ou à la fin
        #  Résultat propre : "Lead Architect"

        date_text = soup.find(string=re.compile(r"Publiée le"))
        date_pub = re.search(r"\d{2}/\d{2}/\d{4}", date_text).group() if date_text else None 
        # Cherche "Publiée le" puis extrait la date au format 05/05/2026, Si pas trouvé → None au lieu de planter

        tags = [a.get_text(strip=True) for a in soup.select("a[href*='/jobs/']")]
        # Récupère les tags compétences cliquables ex: ["PHP", "Drupal", "CSS"]

        sections = {}
        for h2 in soup.find_all("h2"):
            titre_section = h2.get_text(strip=True)
            contenu = []
            for sibling in h2.find_next_siblings():
                if sibling.name == "h2":
                    break
                contenu.append(sibling.get_text(strip=True))
            sections[titre_section] = " ".join(contenu)
            #  Boucle sur tous les titres <h2> de la page, Pour chaque titre, récupère tout le texte qui suit jusqu'au prochain <h2>, Résultat : {"Profil recherché": "Bac+5...", "Environnement de travail": "..."} python

        
        # Localisation depuis og:title
        og_title = soup.find("meta", property="og:title")
        ville = ""
        region = ""

        if og_title:
            contenu = og_title.get("content", "")
            # Extrait ce qui est juste avant "| Free-work"
            match = re.search(r'[\—\-]\s*([\w\s\(\)\-\.]+?)\s*\|\s*Free-work', contenu)
            if match:
                ville = match.group(1).strip()
                # Nettoie les numéros de département ex: "Lyon (69)" → "Lyon"
                ville = re.sub(r'\s*\(\d+\)', '', ville).strip()

            loc_tag = soup.find("span", attrs={"title": re.compile(r".+, .+")})
            print(f"DEBUG localisation : {loc_tag}")  # ← ajoute ça

        return {
            "titre": titre,
            "date_publication": date_pub,
            "competences_tags": tags,
            "profil": sections.get("Profil recherché", ""), # Retourne uniquement les 4 champs qui nous intéressent
            "ville": ville,
            "region": region
        }

    except Exception as e:
        print(f"Erreur : {e}")
        return None #  Si quoi que ce soit plante sur cette offre → on affiche l'erreur et on continue sans bloquer tout le script


def get_all_offer_urls(nb_pages=3):
    all_urls = []
    for page in range(1, nb_pages + 1): # boucle de la page 1 à page 555
        print(f"Scraping page {page}/{nb_pages}...")
        url = f"{BASE_URL}/fr/tech-it/jobs?page={page}"  # Construit l'URL de chaque page ex: .../jobs?page=1, .../jobs?page=2...
        try:
            soup = BeautifulSoup(requests.get(url, headers=HEADERS).text, "html.parser") # Télécharge la page et la rend lisible
            liens = soup.select("a[href*='/job-mission/']") # Cherche tous les liens qui contiennent /job-mission/ → ce sont les liens vers les offres
            urls = list(set([BASE_URL + a["href"] for a in liens if a.get("href")]))
            all_urls.extend(urls) 
            # Construit les URLs complètes et les ajoute à la liste globale et set() évite les doublons
            print(f"  → {len(urls)} offres trouvées")
        except Exception as e:
            print(f"Erreur page {page} : {e}")
        time.sleep(random.uniform(1, 3)) # Pause aléatoire entre 1 et 3 secondes avant la page suivante → évite le blocage
    return list(set(all_urls)) #  Retourne toutes les URLs sans doublons (~8867 URLs)


def scrape_all_offers():
    print("=== Étape 1 : Récupération des URLs ===")
    urls = get_all_offer_urls(nb_pages=1)
    print(f"\nTotal URLs trouvées : {len(urls)}")

    print("\n=== Étape 2 : Scraping des offres ===")
    offres = []
    for i, url in enumerate(urls): #  Boucle sur chaque URL récupérée à l'étape 1 'enumerate' donne aussi le numéro i pour afficher la progression
        print(f"Offre {i+1}/{len(urls)}")
        offre = scrape_freework_offer(url) # Appelle la fonction qui scrape le détail de l'offre
        
        # FILTRE - offres françaises uniquement
        pays_exclus = ["Suisse", "Belgique", "España", "Luxembourg"]
        if offre and offre.get("region", "") not in pays_exclus:
            offres.append(offre)

        if i % 100 == 0 and i > 0: #  "toutes les 100 offres (100, 200, 300...), sauf au début"
            with open("offres_freework_backup.json", "w", encoding="utf-8") as f:
                json.dump(offres, f, ensure_ascii=False, indent=2) # "Sauvegarde ma liste d’offres dans un fichier JSON, proprement formaté et lisible"
            print(f"  → Backup sauvegardé ({len(offres)} offres)")
        time.sleep(random.uniform(1, 2)) # pause entre chaque offre - on évite le blocage

    with open("offres_freework.json", "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2) #  Sauvegarde finale de toutes les offres dans un fichier JSON ( pas de doublon)
    

    print(f"\n✅ Terminé ! {len(offres)} offres sauvegardées")
    return offres


if __name__ == "__main__":
    scrape_all_offers()