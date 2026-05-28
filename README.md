# ObservIA
Brief Simplon ObservIA

## Création et initialisation de l'environnement
py 3.14.2 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

## Initialisation du projet
Ajouter les données csv au dossier data/datagouv
Ajouter la table de correspondances avec le nom table-correspondance-rome-rncp.csv au dossier data/datagouv

## Données formations.csv
Colonnes :

annee_mois
code_rncp
intitule_certification
entrees_formation

Nombre de lignes : 2942 sans en-tête

## Données correspondances.csv
Colonnes :

code_rome
intitule_rome
code_rncp
intitule_rncp
niveau_rncp

Nombre de lignes : 313 sans en-tête