from extractors.sirets import load_sirets

def add_zone_column(dataframe):
    sirets = load_sirets()
    correspondance = dict(zip(sirets["siret"], sirets["location"]))
    dataframe["zone"] = dataframe["siret_of_contractant"].map(correspondance)
    return dataframe
