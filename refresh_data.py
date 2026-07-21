"""
Script pour réextraire les données job_offers.csv
Supprime l'ancienne version et relance le scrapping
"""
import os
from compute_freework_offers import compute_freework_offers

# Fichiers à supprimer pour forcer la réextraction
files_to_remove = [
    "job_offers.csv",
    "result/freework_offers.csv"
]

print("🔄 Suppression des anciennes données...")
for file_path in files_to_remove:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"   ✓ Supprimé: {file_path}")
    else:
        print(f"   - Fichier introuvable: {file_path}")

print("\n⬇️  Réextraction des données Freework...")
compute_freework_offers()

print("\n✅ Extraction terminée!")
