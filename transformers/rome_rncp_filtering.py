def filter_data(formations, correspondances):
    formations = formations.drop(columns=["annee", "mois", "type_referentiel", "code_rs", "code_certifinfo", "raison_sociale_of_contractant", "sorties_realisation_partielle", "date_chargement"])
    formations = formations[formations["code_rncp"] != -1]
    formations = formations[formations["entrees_formation"] > 0]

    correspondances = correspondances[correspondances["code_rome"].str.contains("M", na=False)]

    correspondances = correspondances.drop(columns=["niveau_rncp", "intitule_rncp"])
    correspondances["code_rncp"] = correspondances["code_rncp"].str.extract(r"(\d+)")[0].astype(int)

    formations = formations[formations["code_rncp"].isin(correspondances["code_rncp"])]
    correspondances = correspondances[correspondances["code_rncp"].isin(formations["code_rncp"])]

    return formations, correspondances
