def get_unique_values(dataframe, column_name):
    unique_values = dataframe[column_name].unique()
    return unique_values