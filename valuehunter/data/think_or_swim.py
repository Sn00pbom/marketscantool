import pandas as pd
from pandas import DataFrame
from io import StringIO


def watchlist_to_namespace(path) -> list:
    with open(path, 'r') as ns_file:
        data = ns_file.read()
        data = data.split('\n')
        data = data[4:-1]
        out = [line.split(',')[0] for line in data]
        return out

def watchlist_to_dataframe(path, index='Symbol') -> DataFrame:
    with open(path, 'r') as file:
        data = file.read()
        file.close()
        data = data.split('\n')
        data = data[3:len(data)-1]
        s = '\n'.join(data)
        df = pd.read_csv(StringIO(s))
        df.set_index(index, inplace=True)
        return df

def to_dataframe(path) -> DataFrame:
    with open(path, 'r') as file:
        data = file.read()
        data = data.split('\n')
        data = data[3:len(data)-1]
        s = '\n'.join(data)
        df = pd.read_csv(StringIO(s))
        return df

