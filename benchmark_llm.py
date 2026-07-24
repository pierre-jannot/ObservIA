import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 1. Charger la clé et se connecter à OpenRouter
load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ---- MODELE A TESTER (change juste cette ligne pour tester un autre modele) ----
MODELE = "nvidia/nemotron-3-ultra-550b-a55b:free"

# nom du fichier de resultats, base sur le modele
nom_fichier = "resultats_" + MODELE.replace("/", "_").replace(":", "_") + ".json"

# 2. Lire l'échantillon
with open("sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# petite fonction : retrouver le nom d'une formation a partir de son id
def nom_formation(candidates, id_cherche):
    for formation in candidates:
        if formation["id_formation"] == id_cherche:
            return formation["intitule_certification"]
    return "(inconnu)"


# 3. Fonction qui traite UNE offre et renvoie son classement (avec les noms)
def classer_une_offre(paire):
    offre = paire["offre"]
    candidates = paire["candidates"]

    liste_formations = ""
    for formation in candidates:
        liste_formations += f"- id {formation['id_formation']} : {formation['intitule_certification']}\n"

    message = f"""Voici une offre d'emploi :
Intitulé : {offre['intitule']}
Code métier (ROME) : {offre['code_rome']}

Voici des formations candidates :
{liste_formations}

Evalue la correspondance de chaque formation avec l'offre.
Réponds UNIQUEMENT avec une liste JSON, sans texte autour, sans markdown, sans balises.
Format exact : [{{"id_formation": <id>, "score": <nombre de 0 à 1>}}]
Classe du score le plus élevé au plus bas."""

    reponse = client.chat.completions.create(
        model=MODELE,
        messages=[{"role": "user", "content": message}],
    )

    if not reponse.choices:
        return []

    texte = reponse.choices[0].message.content
    classement = json.loads(texte)

    # ajouter le NOM de chaque formation a cote de son id
    for item in classement:
        item["nom_formation"] = nom_formation(candidates, item["id_formation"])

    return classement


# 4. Boucle sur les 50 offres
resultats = []
paires = data["pairs"]
nb_reussies = 0
nb_ratees = 0

debut = time.time()  # depart du chronometre

for i, paire in enumerate(paires):
    offre = paire["offre"]
    print(f"[{i+1}/{len(paires)}] {offre['intitule']}")

    try:
        classement = classer_une_offre(paire)
        nb_reussies += 1
    except Exception as erreur:
        print("   /!\\ offre ratee :", erreur)
        classement = []
        nb_ratees += 1

    resultats.append({
        "offre_id": offre["id"],
        "offre_intitule": offre["intitule"],
        "classement": classement,
    })

    # objet complet a sauvegarder (avec le temps ecoule jusqu'ici)
    sortie = {
        "modele": MODELE,
        "duree_secondes": round(time.time() - debut, 1),
        "nb_reussies": nb_reussies,
        "nb_ratees": nb_ratees,
        "resultats": resultats,
    }

    # SAUVEGARDE DE SECOURS a chaque offre (on ne perd jamais ce qui est fait)
    with open(nom_fichier, "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=2)

    time.sleep(4)

# 5. Bilan
print("\nTermine !")
print(nb_reussies, "offres reussies /", nb_ratees, "ratees")
print("Duree totale :", sortie["duree_secondes"], "secondes")
print("Resultats sauvegardes dans :", nom_fichier)
