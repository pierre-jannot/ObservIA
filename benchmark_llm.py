import json 
import os 
from openai import OpenAI
from dotenv import load_dotenv 

# charger la clé depuis le .env
load_dotenv()
cle = os.getenv ("OPENROUTER_API_KEY")

# préparer la connexion à OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=cle,
)

#  lire l'échantillon
with open ("sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# prendre la premiere offre et ses formations
paire = data["pairs"][0]
offre = paire["offre"] 
candidates = paire["candidates"]

# construire la liste des formations en texte
liste_formations = ""
for f in candidates:
    liste_formations += f"- id {f['id_formation']} : {f['intitule_certification']}\n"

# ecrire le message pour l'IA
message = f"""Voici une offre d'emploi : 
Intitulé : {offre['intitule']}
code métier (ROME) : {offre['code_rome']}

voici des formations candidats: 
{liste_formations}

Evalue la correspondance de chaque formation avec l'offre.
Réponds UNIQUEMENT avec une liste JSON, sans texte autour, sans markdown, sans balises.
Format exacte : [{{"id_formation": <id>, "score": <nombre de 0 à 1>}}]
Classe du score le plus élevé au plus bas.""" 


# Envoyer à l'IA
reponse = client.chat.completions.create(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    messages=[{"role": "user", "content": message}],
)

# récup texte de la réponse
texte_reponse = reponse.choices[0].message.content

# transformer le texte en données Python 
classement = json.loads(texte_reponse)

# afficher proprement
print("classement pour l'offre:", offre["intitule"])
for item in classement:
    intitule = ""
    for formation in candidates: 
        if formation["id_formation"] == item["id_formation"]:
            intitule = formation["intitule_certification"]
            break
    print(" Formation", item["id_formation"], ":", intitule, "score", item["score"])

