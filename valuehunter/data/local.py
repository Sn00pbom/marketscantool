from pandas import DataFrame
import pandas as pd

def namespace_from_tab_delimited(path) -> list:
    return list(df_from_tab_delimited(path)['Symbol'].values)

def namespace_from_symbol_list(path) -> list:
    with open(path, 'r') as f:
        data = f.read()
        return data.split('\n')

def df_from_tab_delimited(path) -> DataFrame:
    return pd.read_csv(path, delimiter='\t')

def get_historical_daily(ticker) -> DataFrame:
    hist_path = 'C:/dataset/amex-nyse-nasdaq-stock-histories/fh_20190420/full_history/{}.csv'.format(ticker)
    df = pd.read_csv(hist_path)
    return df

def get_all_earnings() -> DataFrame:
    earnings_path = "C:/dataset/us-historical-stock-prices-with-earnings-data/stocks_latest/earnings_latest.csv"
    earnings_df = pd.read_csv(earnings_path)
    return earnings_df

def get_ticker_earnings(all_earnings_df:DataFrame, ticker:str) -> DataFrame:
    return all_earnings_df[all_earnings_df['symbol'] == ticker]

def get_all_earnings_summary() -> DataFrame:
    path = "C:/dataset/us-historical-stock-prices-with-earnings-data/dataset_summary.csv"
    df = pd.read_csv(path)
    return df

def namespace_from_summary(summary_df:DataFrame) -> list:
    return list(summary_df['symbol'].values)
