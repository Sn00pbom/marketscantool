from pandas import DataFrame
import pandas as pd
from valuehunter import config


def namespace_from_tab_delimited(path) -> list:
    return list(df_from_tab_delimited(path)['Symbol'].values)


def namespace_from_symbol_list(path) -> list:
    with open(path, 'r') as f:
        data = f.read()
        return data.split('\n')


def df_from_tab_delimited(path) -> DataFrame:
    return pd.read_csv(path, delimiter='\t')


def get_price_history(ticker: str) -> DataFrame:
    hist_path = 'C:/dataset/amex-nyse-nasdaq-stock-histories/fh_20190420/full_history/{}.csv'.format(ticker)
    return pd.read_csv(hist_path, parse_dates=['date'])


def get_ticker_earnings(ticker: str, all_earnings_df: DataFrame = None) -> DataFrame:
    if all_earnings_df is None:
        all_earnings_df = get_all_earnings()

    return all_earnings_df[all_earnings_df['symbol'] == ticker]


def get_all_earnings() -> DataFrame:
    return pd.read_csv(config.ALL_EARNINGS_PATH)


def get_all_prices() -> DataFrame:
    return pd.read_csv(config.ALL_PRICES_PATH)


def get_dataset_summary() -> DataFrame:
    """Returns dataset summary with from and to dates indexed by 'symbol'. All column names are lower-case"""
    path = "C:/dataset/us-historical-stock-prices-with-earnings-data/dataset_summary.csv"
    df = pd.read_csv(path)
    df = df.set_index('symbol')
    return df


def namespace_from_summary(summary_df:DataFrame) -> list:
    return list(summary_df['symbol'].values)


def dict_from_csv(path: str) -> dict:
    with open(path, 'r') as f:
        d = f.read()
        lines = d.split('\n')
        for i in range(len(lines)):
            lines[i] = lines[i].split(',')

        columns = lines.pop(0)
        lines.pop()
        data = {val: [] for val in columns}
        for line in lines:
            for i in range(len(columns)):
                data[columns[i]].append(line[i])

        return data
