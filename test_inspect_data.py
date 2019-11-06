import pandas as pd
import valuehunter as vh
from yahoo_finance_api2 import share

FOLDER = './dat/temp'
def get_path(ticker):
    return './dat/temp/' + ticker + '.data.csv'
namespace = vh.data.NameSpace.from_tos_wl('./dat/2019-11-05-watchlist.csv')
namespace._vals = namespace._vals[:10]
data_dict = vh.data.get_namespace_historical(namespace, share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_DAY, 1)
for ticker in data_dict:
    l = data_dict[ticker].shape[0]
    print(ticker, l)
