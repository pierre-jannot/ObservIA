# ObservIA
Brief Simplon ObservIA

## Création et initialisation de l'environnement
```bash
py 3.14.2 -m venv .ven
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ajout des variables d'environnement
Copier le .env.example en .env et remplir les champs avec les informations de l'API France Travail

## Ajout des données csv
Ajouter les données csv au dossier data/datagouv
Ajouter la table de correspondances avec le nom table-correspondance-rome-rncp.csv au dossier data/datagouv

## Initialisation du projet

Pour lancer le projet, il est nécessaire de suivre une des deux opérations ci-dessous. Une fois exécuté, l'API devrait être accessible depuis http://localhost:8000/docs

### Exécution depuis Python
Dans le dossier du projet, au même niveau que le main, exécuter
```bash
uvicorn main:app --reload --port 8000
```

### Exécution depuis Docker
Dans le dossier du projet, au même niveau que le Dockerfile, exécuter
```bash
docker compose up --build
```

## Données formations.csv
Colonnes :

annee_mois
code_rncp
intitule_certification
siret_of_contractant
entrees_formation

Nombre de lignes : 2942 sans en-tête

## Données correspondances.csv
Colonnes :

code_rome
intitule_rome
code_rncp

Nombre de lignes : 313 sans en-tête