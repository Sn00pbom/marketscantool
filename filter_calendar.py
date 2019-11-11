import sys
import valuehunter
import pandas as pd


if valuehunter.config.DEBUG:
    after_s = '11/12/19'
    before_s = '11/13/19'
    path = './dat/calendar.csv'
else:
    if not len(sys.argv) is 4:
        print('python filter_calendar.py [CALENDAR PATH] [AFTER DATE] [BEFORE DATE]')
        exit()
    path = sys.argv[1]
    after_s = sys.argv[2]
    before_s = sys.argv[3]

df = valuehunter.data.load_tos_data(path)
namespace = list(df.index)
sieve = valuehunter.sieve.Sieve(lambda ticker:
        (df.at[ticker, 'Time est'] == 'After Market' and df.at[ticker, 'Date est'] == after_s)
        or
        (df.at[ticker, 'Time est'] == 'Before Market' and df.at[ticker, 'Date est'] == before_s))
pd.DataFrame(sieve.sift(namespace)).to_clipboard(index=False, header=False)
print('Copied all filtered tickers to clip-board.')