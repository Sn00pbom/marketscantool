from yahoo_finance_api2 import share
import pandas as pd
from finta import TA
import datetime
import numpy as np
import sys
import valuehunter as vh

if vh.config.DEBUG:
    PATH = './dat/2019-11-03-watchlist.csv'
else:
    if len(sys.argv) is 2:
        PATH = sys.argv[1]
    else:
        print('USAGE: python score_wl_macd_thresh_chain.py [PATH TO WATCHLIST]')
        exit()
print('Starting...')
namespace = vh.data.NameSpace.from_tos_wl(PATH)
wl_data = vh.data.load_tos_data(PATH)
print('Ticker namespace loaded.')

THRESH_PERCENT = .8
print('Loading historical data from Yahoo!...')
data_dict = vh.data.get_namespace_historical(namespace,
    share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_DAY, 1)
print('Finished.')

print('Computing MACDs...')
for ticker in data_dict:
    ticker_df = data_dict[ticker]
    macd_df = TA.MACD(ticker_df)
    for key in macd_df:
        ticker_df[key] = macd_df[key]
    ticker_df['HISTOGRAM'] = macd_df['MACD'] - macd_df['SIGNAL']

print('Compiling DataFrame and saving to file...')

rubrick = {
    'Threshold': {
        'f': lambda data_dict, ticker: vh.grade.score_thresh_macd(data_dict[ticker], THRESH_PERCENT),
        'perfect': 1.0,
        'weight': 65.0
    },
    'Chain Len': {
        'f': lambda data_dict, ticker: vh.grade.histogram_reversal_chain(data_dict[ticker], l=3),
        'perfect': 10.0,
        'weight': 35.0
    }
}
my_grader = vh.grade.Grader(rubrick)
score_sheet = my_grader.grade(data_dict)
for col in wl_data:
    score_sheet[col] = wl_data[col]

path = vh.config.SCAN_FOLDER_PATH + 'SCAN-' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M') + '.csv'
score_sheet.to_csv(path)
print('Saved to',path)