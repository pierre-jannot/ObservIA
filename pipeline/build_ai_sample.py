"""Module pour la construction de l'échantillon de test du benchmark."""

import json
import sys
import pandas as pd
from pathlib import Path

from db.repositories.formation_repository import get_unique_formations
from db.repositories.offers_repository import get_random_offers

# On définit proprement le dossier racine 'benchmark'
current_script_path = Path(__file__).resolve()
parent_dir = current_script_path.parent.parent  # C'est le dossier 'benchmark'

sys.path.append(str(parent_dir))

NB_OFFRES_PER_SOURCE = 125  # 125 Scraping + 125 FT = 250 offres au total

TABLE_SCRAPING = "scraping"
TABLE_FT = "offre_france_travail"


def fetch_formations():
    """Récupère toutes les formations uniques optimisées depuis la base."""
    formations_df = get_unique_formations()
    formations_df["intitule_certification"] = (
        formations_df["intitule_certification"].str.strip()
        )

    formations_df["code_rncp"] = (
        formations_df["code_rncp"].astype(str).str.strip()
        )

    formations = formations_df.to_dict("records")

    return formations


def fetch_random_offers(source: str) -> list[dict]:
    """Récupère un échantillon aléatoire d'offres et le normalise."""

    print(f"Récupération de {NB_OFFRES_PER_SOURCE} offres '{source}'...")

    df = get_random_offers(NB_OFFRES_PER_SOURCE, source)

    if df.empty:
        print(f"   - Aucune offre {source} trouvée.")
        return []

    # Nettoyage des champs texte
    titre = df["title"].fillna("").str.strip()
    profil = df["description"].fillna("").str.strip()

    # Construction du DataFrame final
    result = pd.DataFrame({
        "id": source.upper() + "_" + df["id_offer"].astype(str),
        "titre": titre,
        "profil": profil,
        "code_rome": (
            df["rome_code"]
            .fillna("")
            .str.strip()
            .replace("", None)
        ),
        "source": source,
        "code_region": df["id_region"],
    })

    # Construction du texte complet
    result["texte_complet"] = result["titre"]

    mask = result["profil"] != ""
    result.loc[mask, "texte_complet"] = (
        result.loc[mask, "titre"] + " - " + result.loc[mask, "profil"]
    )

    print(f"   - {len(result)} offres '{source}' chargées.")

    return result.to_dict(orient="records")


def save_sample_to_json(formations, offres):
    """Sauvegarde l'échantillon final dans un fichier JSON structuré."""
    sample_data = {
        "metadata": {
            "nb_formations": len(formations),
            "nb_offres_totales": len(offres),
            "nb_offres_freework": sum(1 for o in offres if o["source"] == "Freework"),
            "nb_offres_france_travail": sum(
                1 for o in offres if o["source"] == "FranceTravail"
            ),
        },
        "formations": formations,
        "offres": offres,
    }

    output_dir = parent_dir / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "sample.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("ECHANTILLON MIS A JOUR ET GENERE !")
    print(f"Formations uniques (Optimisees) : {len(formations)}")
    print(f"Offres Totales (Echantillon)    : {len(offres)}")
    print(f"   - Freework                 : {sample_data['metadata']['nb_offres_freework']}")
    print(f"   - France Travail           : {sample_data['metadata']['nb_offres_france_travail']}")
    print(f"Fichier de sortie               : {output_path}")
    print("=" * 60)


def build_sample():
    """Coordonne l'extraction et l'export de l'échantillon de test."""

    formations_df = get_unique_formations()

    formations_df["title"] = (
        formations_df["title"].str.strip()
    )

    formations_df = formations_df.rename(columns={"title": "titre"})

    formations_df["code_rncp"] = (
        formations_df["code_rncp"].astype(str).str.strip()
    )

    formations = formations_df.to_dict(orient="records")

    offres = (
        fetch_random_offers("Freework")
        + fetch_random_offers("FranceTravail")
    )

    save_sample_to_json(formations, offres)


if __name__ == "__main__":
    build_sample()