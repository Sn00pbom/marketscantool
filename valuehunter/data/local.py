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
    hist_path = '{}{}.csv'.format(config.SYMBOL_HISTORY_PATH, ticker)
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
    df = pd.read_csv(config.SUMMARY_PATH)
    df = df.set_index('symbol')
    return df


def namespace_from_summary(summary_df: DataFrame) -> list:
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


def multi_df_to_excel(path: str, dfs: list, names: list = None, index=False):
    if names and len(dfs) is not len(names):
        raise ValueError('Lists must be same size')

    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        # Write each dataframe to a different worksheet.
        for i, df in enumerate(dfs):
            df.to_excel(writer, sheet_name='Sheet'+str(i+1) if not names else names[i], index=index)

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

