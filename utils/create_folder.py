import os

def create_folder(path):
    if os.path.exists(path):
        return
    else:
        os.mkdir(path)
        print(f"Dossier {path} créé avec succès.")