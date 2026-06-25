from utils.compute_dataframe import get_quarter_values, sum_values

def column_per_quarter(dataframe, column):
    dataframe = get_quarter_values(dataframe, "annee_mois")
    dataframe = sum_values(dataframe, column, "quarter")
    result = [
        {"trimestre": str(index), f"nombre_{column}": int(value)}
        for index, value in dataframe.items()
    ]
    return result