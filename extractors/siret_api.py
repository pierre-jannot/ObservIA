import requests

def get_region_from_siret(siret: str) -> dict:
    r = requests.get(
        "https://recherche-entreprises.api.gouv.fr/search",
        params={"q": siret, "mtm_campaign": "annuaire"}
    )
    result = r.json()["results"][0]
    siege = result["siege"]
    return {
        "siret": siret,
        "nom_raison_sociale": result["nom_raison_sociale"],
        "code_postal": siege["code_postal"],
        "region":      siege["region"],
    }