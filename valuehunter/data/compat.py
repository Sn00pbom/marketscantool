import pandas as pd
from pandas import DataFrame, Series
from datetime import datetime

# The goal of this module is to provide a standard for the DataFrames used in the functions in the package.

def capitalize_column_names(df:DataFrame) -> DataFrame:
    return df.rename(columns={column:column.capitalize for column in df.columns})

def standardize_date(unformatted_date:str):
    # format to MM-DD-YYYY hh:mm
    pass

def standardize_time_column(s:Series) -> Series:
    return s.apply(standardize_date)