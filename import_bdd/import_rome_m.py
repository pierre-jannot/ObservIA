import os
import csv
import psycopg2
from psycopg2 import errors
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Recuperation des parametres de configuration PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "ObservIA")

CONN_PARAMS = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME
}

def importer_codes_rome_m(chemin_csv):
    print("Connexion a la base de donnees pour l'import des codes ROME...")
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Erreur de connexion a la base de donnees : {e}")
        return

    compteur_rome = 0
    compteur_rncp = 0

    print(f"Lecture du fichier {chemin_csv} et filtrage des codes commençant par 'M'...")
    
    with open(chemin_csv, "r", encoding="utf-8-sig") as fichier:
        # On utilise le point-virgule comme vu dans ton script precedent
        lecteur = csv.DictReader(fichier, delimiter=";")
        
        for ligne in lecteur:
            code_rome = ligne.get("code_rome")
            intitule_rome = ligne.get("intitule_rome")
            code_rncp_str = ligne.get("code_rncp")

            # On verifie que le code existe et commence bien par 'M' (ou 'm')
            if not code_rome or not code_rome.upper().startswith("M"):
                continue

            code_rome_formatte = code_rome.upper().strip()

            
            query_rome = """
            INSERT INTO correspondance_rome_rncp (code_rome, intitule_rome)
            VALUES (%s, %s)
            ON CONFLICT (code_rome) DO NOTHING;
            """
            
            try:
                # On passe [code_rome_formatte] sous forme de liste pour remplir le type VARCHAR(5)[]
                cursor.execute(query_rome, (code_rome_formatte, intitule_rome))
                if cursor.rowcount > 0:
                    compteur_rome += 1
            except Exception as e:
                print(f"Erreur lors de l'insertion du code ROME {code_rome_formatte} : {e}")
                conn.rollback()
                continue

            # 2. Insertion dans la table de liaison : rncp_rome (si un code RNCP est present)
            if code_rncp_str and code_rncp_str.strip().isdigit():
                code_rncp = int(code_rncp_str.strip())
                
                query_rncp = """
                INSERT INTO rncp_rome (code_rome, code_rncp)
                VALUES (%s, %s)
                ON CONFLICT (code_rome, code_rncp) DO NOTHING;
                """
                
                try:
                    cursor.execute(query_rncp, (code_rome_formatte, code_rncp))
                    if cursor.rowcount > 0:
                        compteur_rncp += 1
                except Exception as e:
                    print(f"Erreur lors de l'insertion de la liaison ROME-RNCP ({code_rome_formatte}, {code_rncp}) : {e}")
                    conn.rollback()
                    continue

        # Validation de toutes les insertions reussies
        conn.commit()
        print(f"\nImportation terminee avec succes !")
        print(f"-> {compteur_rome} nouveaux codes ROME (commençant par M) inseres.")
        print(f"-> {compteur_rncp} nouvelles relations ROME-RNCP inserees.")

        cursor.close()
        conn.close()

if __name__ == "__main__":
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    dossier_racine = os.path.dirname(dossier_actuel)
    nom_fichier_csv = os.path.join(dossier_racine, 'result', 'correspondances.csv')
    
    if os.path.exists(nom_fichier_csv):
        importer_codes_rome_m(nom_fichier_csv)
    else:
        print(f"Erreur : Le fichier '{nom_fichier_csv}' est introuvable dans le dossier actuel.")