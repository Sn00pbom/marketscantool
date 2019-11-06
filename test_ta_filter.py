from sieve import Sieve
import data_man
from yahoo_finance_api2 import share
from finta import TA

namespace = data_man.load_namespace_from_file('namespace.txt')
data_dict = data_man.get_namespace_historical(namespace,
    share.PERIOD_TYPE_YEAR, 1,
    share.FREQUENCY_TYPE_DAY, 1
)


def macd_percent_highest_threshold(ticker, percent, n_days):
    global data_dict
    data = data_dict[ticker]
    macd_data = TA.VW_MACD(ohlcv=data)
    highest = macd_data['MACD'].max()
    thresh = highest * percent
    macd_tail = macd_data.tail(n_days)
    for _, row in macd_tail.iterrows():
        # print(row[1])
        if row['MACD'] >= thresh:
            return True
    return False


my_sieve = Sieve(lambda ticker : macd_percent_highest_threshold(ticker, .8, 5), )
output = my_sieve.sift(data_dict)
s_out = ''
# TODO build output to file functions
print(output)
