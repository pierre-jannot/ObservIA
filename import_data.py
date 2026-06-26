import os
import subprocess
import sys

def lancer_scripts_import():
    dossier_obseria = os.path.dirname(os.path.abspath(__file__))
    dossier_import = os.path.join(dossier_obseria, 'import_bdd')
    
    if not os.path.exists(dossier_import):
        print(f"Erreur : Le dossier '{dossier_import}' est introuvable.")
        return

    scripts = [
        "import_rome_m.py",
        "import_rncp_rome.py",
        "import_departments.py",
        "import_sirets.py",
        "import_formations.py",
        "import_scraping.py",
        "api_FranceTravail_to_BDD.py"
    ]

    print(f"Debut de l'execution globale des {len(scripts)} scripts d'importation...\n")

    for i, script in enumerate(scripts, 1):
        chemin_complet = os.path.join(dossier_import, script)
        
        if not os.path.exists(chemin_complet):
            print(f"[Fichier introuvable] {script} n'existe pas dans import_bdd/. Passage au suivant.")
            continue

        print(f"=========================================")
        print(f" [{i}/{len(scripts)}] Lancement de : {script}")
        print(f"=========================================")
        
        try:
            # AVANT : cwd=dossier_import  →  les scripts cherchaient leurs fichiers dans import_bdd/
            # APRES : cwd=dossier_obseria →  les chemins relatifs se resolvent depuis la racine du projet
            subprocess.run([sys.executable, chemin_complet], check=True, cwd=dossier_obseria)
            print(f"\n{script} termine avec succes.\n")
            
        except subprocess.CalledProcessError as e:
            print(f"\nErreur critique dans {script} (Code de sortie: {e.returncode}).")
            reponse = input("Voulez-vous continuer avec les scripts suivants ? (o/n) : ")
            if reponse.lower() != 'o':
                print("Arret du script maitre.")
                break

    print("Tout le processus d'importation est termine !")

if __name__ == "__main__":
    lancer_scripts_import()