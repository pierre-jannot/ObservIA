from collections import Counter
import json

with open("data/datagouv/entree_sortie_formation.csv", "r", encoding='utf-8') as f:
    formations = f.read()
    formations = formations.split('\n')
    for i in range(len(formations)):
        formations[i] = formations[i].split(';')

formations_list = []

for i in range(len(formations)-2):
    line = formations[i+1]
    annee_mois = line[0]
    type_referentiel = line[3]
    code_rncp = line[4]
    code_rs = line[5]
    intitule_certification = line[7]

    formations_list.append(
        {
            "intitule_certification": intitule_certification,
            "type_referentiel": type_referentiel,
            "code_rncp": code_rncp,
            "code_rs": code_rs,
            "annee_mois": annee_mois
        }
    )

compteur = Counter(ligne["intitule_certification"] for ligne in formations_list)