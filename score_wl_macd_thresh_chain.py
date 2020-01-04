import datetime
import argparse

from yahoo_finance_api2 import share
from finta import TA

import valuehunter as vh


def score_macd_thresh_chain(namespace):

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

    print('Compiling DataFrame...')

    rubrick = vh.grade.Rubric()
    rubrick.add_column('Threshold',
                       lambda dd, t: vh.grade.macd.score_thresh_macd(dd[t], THRESH_PERCENT),
                       1.0, 35.0)
    rubrick.add_column('Chain Len',
                       lambda dd, t: vh.grade.macd.histogram_chain(dd[t]['HISTOGRAM'].values,
                                                                   look_back=2, reversal=True),
                       10.0, 65.0)

    my_grader = vh.grade.Grader(rubrick)
    score_sheet = my_grader.grade(data_dict)
    my_grader.rubric['Chain Len']['f'] = lambda dd, t: vh.grade.macd.histogram_chain(dd[t]['HISTOGRAM'].values,
                                                                                     look_back=2, reversal=False)
    tss = my_grader.grade(data_dict)
    score_sheet['Chain Len(No Reversal)'] = tss['Chain Len']
    score_sheet['Composite Score(No Reversal)'] = tss['Composite Score']

    return score_sheet


def run_with_wl_values(pargs=None):
    args = parse_args(pargs)
    print('Starting...')
    namespace = vh.data.think_or_swim.watchlist_to_namespace(args.path)
    print('Ticker namespace loaded.')

    score_sheet = score_macd_thresh_chain(namespace)

    wl_data = vh.data.think_or_swim.watchlist_to_dataframe(args.path)
    for col in wl_data:
        score_sheet[col] = wl_data[col]

    return score_sheet


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(description='Get a score sheet of a set of tickers in a Think or Swim watch list.')

    parser.add_argument('path', nargs=1,
                        metavar='PATH',
                        help='path to think or swim watchlist file.')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    # TODO move format string to config
    score_sheet = run_with_wl_values()
    print('Saving to file...')
    path = vh.config.SCAN_FOLDER_PATH + 'SCAN-' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M') + '.csv'
    score_sheet.to_csv(path)
    print('Saved to', path)
