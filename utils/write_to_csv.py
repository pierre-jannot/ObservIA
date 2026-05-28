import os

def write_dataframe(path, dataframe):
    if os.path.exists(path):
        print(f"Données {path} existantes. Réécriture des données ignorée.")
    else:
        dataframe.to_csv(path, sep=";", index=False, encoding="utf-8")
        print(f"Données {path} écrites avec succès.")