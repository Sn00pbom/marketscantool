import pandas as pd
import valuehunter as vh
from yahoo_finance_api2 import share
from finta import TA

# namespace = vh.data.namespace.from_tos_wl('./dat/2019-11-05-watchlist.csv')
namespace = vh.data.namespace.from_text_file('./namespace.txt')
data_dict = vh.data.get_namespace_historical(namespace, share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_DAY, 1)
for ticker in data_dict:
    l = data_dict[ticker].shape[0]
    print(data_dict[ticker])
    print(ticker, l)
aapl = data_dict['AAPL']
macd = TA.MACD(aapl)