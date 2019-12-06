from yahoo_finance_api2 import share
from finta import TA
import datetime
import sys
import valuehunter as vh

if vh.config.DEBUG:
    PATH = './dat/small_wl.csv'
else:
    if len(sys.argv) is 2:
        PATH = sys.argv[1]
    else:
        print('USAGE: python score_wl_macd_thresh_chain.py [PATH TO WATCHLIST]')
        exit()
print('Starting...')
namespace = vh.data.think_or_swim.watchlist_to_namespace(PATH)
wl_data = vh.data.think_or_swim.watchlist_to_dataframe(PATH)
print('Ticker namespace loaded.')

THRESH_PERCENT = .8
print('Loading historical data from Yahoo!...')
data_dict = vh.data.yahoo.get_namespace_historical(namespace,
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

rubrick = vh.grade.Rubrick()
rubrick.add_column('Threshold', lambda data_dict, ticker: vh.grade.macd.score_thresh_macd(data_dict[ticker], THRESH_PERCENT), 1.0, 35.0)
# rubrick.add_column('Chain Len', lambda data_dict, ticker: vh.grade.macd.histogram_chain(data_dict[ticker], L=2, reversal=True), 1.0, 65.0)
rubrick.add_column('Chain Len', lambda data_dict, ticker: vh.grade.macd.histogram_chain(data_dict[ticker]['HISTOGRAM'].values, L=2, reversal=True), 10.0, 65.0)

my_grader = vh.grade.Grader(rubrick)
score_sheet = my_grader.grade(data_dict)
my_grader.rubrick['Chain Len']['f'] = lambda data_dict, ticker: vh.grade.macd.histogram_chain(data_dict[ticker]['HISTOGRAM'].values, L=2, reversal=False)
tss = my_grader.grade(data_dict)
score_sheet['Chain Len(No Reversal)'] = tss['Chain Len']
score_sheet['Composite Score(No Reversal)'] = tss['Composite Score']
for col in wl_data:
    score_sheet[col] = wl_data[col]

# TODO move format string to config
path = vh.config.SCAN_FOLDER_PATH + 'SCAN-' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M') + '.csv'
score_sheet.to_csv(path)
print('Saved to', path)
