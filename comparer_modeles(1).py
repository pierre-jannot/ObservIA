import json
import glob

# 1. Trouver tous les fichiers de resultats (un par modele)
fichiers = glob.glob("resultats_*.json")

if not fichiers:
    print("Aucun fichier de resultats trouve.")
    print("Lance d'abord benchmark_llm.py avec un modele.")
    exit()

# 2. Afficher un tableau comparatif
print("=" * 65)
print("COMPARAISON DES MODELES")
print("=" * 65)

for fichier in fichiers:
    with open(fichier, "r", encoding="utf-8") as f:
        sortie = json.load(f)

    modele = sortie["modele"]
    duree = sortie["duree_secondes"]
    nb_reussies = sortie["nb_reussies"]
    nb_ratees = sortie["nb_ratees"]

    print("\nModele :", modele)
    print("  Offres reussies :", nb_reussies)
    print("  Offres ratees   :", nb_ratees)
    print("  Duree totale    :", duree, "secondes")
    if nb_reussies > 0:
        print("  Temps par offre :", round(duree / nb_reussies, 1), "secondes")

print("\n" + "=" * 65)
