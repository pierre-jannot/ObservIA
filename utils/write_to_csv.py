import os

def write_dataframe(path, dataframe, method="w"):
    if method == "w":
        if os.path.exists(path):
            print(f"Données {path} existantes. Réécriture des données ignorée.")
        else:
            dataframe.to_csv(path, sep=";", index=False, encoding="utf-8")
            print(f"Données {path} écrites avec succès.")
    elif method == "a":
        dataframe.to_csv(path, mode="a", header=not os.path.exists(path), sep=";", index=False, encoding="utf-8")
    else:
        print(f"Method {method} unknown.")
