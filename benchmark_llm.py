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

Pour chaque formation, indique si elle correspond à l'offre et donne un score de 0 à 1.
Classes-les de la plus pertinente à la moins pertinente
Si aucune ne correspond vraiment, dis-le clairement"""

# Envoyer à l'IA
reponse = client.chat.completions.create(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    messages=[{"role": "user", "content": message}],
)

# afficher reponse
print(reponse.choices[0].message.content)



# # lire l'échantillon 
# with open("sample.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# # Vérifier ce qu'on a 
# print("Nombre de paires:", len(data["pairs"]))

# #  afficher la première offre et ses formations 
# premiere_paire = data["pairs"][0]
# offre = premiere_paire["offre"]
# candidates = premiere_paire["candidates"]

# print("\nOffre :", offre["intitule"])
# print("Code ROME :", offre["code_rome"], "/ Région :", offre["code_region"])
# print ("\nFORMATIONS CANDIDATES :")
# for formation in candidates: 
#     print("  -", formation["intitule_certification"],
#           "(région", formation["code_region"] + ")") 

                         