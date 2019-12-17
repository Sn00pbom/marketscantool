import pandas as pd
from pandas import DataFrame


def only_trades_df(df: DataFrame) -> DataFrame:
    return df[df['wl ratio'] != 'NO TRADES']


def pos_dur_avg(df: DataFrame) -> float:
    o = pd.to_datetime(df['open@'])
    c = pd.to_datetime(df['close@'])
    diff = c - o
    return diff.mean()


SCHEME = {
    'nsymbols': lambda d: len(d['Trade Summary'].index),
    'ntrades_avg': lambda d: d['Trade Summary']['n trades'].mean(),
    'wl ratio avg': lambda d: only_trades_df(d['Trade Summary'])['wl ratio'].mean(),
    'pnl avg': lambda d: only_trades_df(d['Trade Summary'])['pnl'].mean(),
    'pnl total': lambda d: only_trades_df(d['Trade Summary'])['pnl'].sum(),
    'pos dur avg': lambda d: pos_dur_avg(d['Trade History']),
}
