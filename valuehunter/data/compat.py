import pandas as pd
from pandas import DataFrame, Series
from datetime import datetime

# The goal of this module is to provide a standard for the DataFrames used in the functions in the package.

def capitalize_column_names(df:DataFrame) -> DataFrame:
    return df.rename(columns={key:key.capitalize() for key in df.columns})

def set_datetime_index(df:DataFrame) -> DataFrame:
    df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)
    return df.set_index(['date'])

def format_df_backtest(df:DataFrame) -> DataFrame:
    # df = df['date'].apply(lambda val: datetime.strptime(val, '%y-%m-%d'))
    # df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)
    # df = df.set_index(['date'])
    df = set_datetime_index(df)
    df = df[['open','close','high','low','volume']]
    df = capitalize_column_names(df)
    return df

