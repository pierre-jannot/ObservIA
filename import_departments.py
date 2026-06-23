import psycopg2
import csv

# Paramètres
DB_CONFIG = {
    "host": "localhost",
    "database": "ObservIA",
    "user": "postgres",
    "password": "TON_MOT_DE_PASSE"
}

def importer_departements():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Nettoyage
        cur.execute("TRUNCATE TABLE localisation;")
        
        with open('departments.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                cur.execute(
                    "INSERT INTO localisation (code_departement, nom_departement, nom_region) VALUES (%s, %s, %s)",
                    (row['code_departement'], row['nom_departement'], row['region'])
                )
        
        conn.commit()
        print("Importation réussie avec Python !")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur fatale : {e}")

if __name__ == "__main__":
    importer_departements()