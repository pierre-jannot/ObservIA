import pandas as pd

def get_unique_values(dataframe, column_name):
    unique_values = dataframe[column_name].unique()
    return unique_values

def get_filtered_values(dataframe, column_name, values):
    filtered_values = dataframe[dataframe[column_name].isin(values)]
    return filtered_values

def get_quarter_values(dataframe, column_name):
    dataframe[column_name] = pd.to_datetime(dataframe[column_name], format="ISO8601", utc=True)
    dataframe["quarter"] = dataframe[column_name].dt.to_period("Q")
    return dataframe

def count_unique_values(dataframe, column_name):
    dataframe = dataframe.groupby(column_name).size()
    return dataframe

def sum_values(dataframe, column_name, group_by_column):
    dataframe = dataframe.groupby(group_by_column)[column_name].sum()
    return dataframe