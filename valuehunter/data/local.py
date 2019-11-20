from pandas import DataFrame
import pandas as pd

def symbol_list_to_namespace(path) -> list:
    with open(path, 'r') as f:
        data = f.read()
        return data.split('\n')

def tab_delimited_to_dataframe(path) -> DataFrame:
    return pd.read_csv(path, delimiter='\t')