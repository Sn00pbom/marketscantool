import sys
import valuehunter
import pandas as pd

if not len(sys.argv) is 4:
    print('python filter_calendar.py [CALENDAR PATH] [AFTER DATE] [BEFORE DATE]')
    exit()

path = sys.argv[1]
after_s = sys.argv[2]
before_s = sys.argv[3]
# after_s = '11/4/19'
# before_s = '11/5/19'
# path = './dat/calendar.csv'
df = valuehunter.data.load_tos_data(path, ['Time', 'Symbol'])
namespace = valuehunter.data.NameSpace(list(df.index))

def fbefore(time):
    return 'Before' in df.at[time, 'Description'] and before_s in df.at[time, 'Description']
def fafter(time):
    return 'After' in df.at[time, 'Description'] and after_s in df.at[time, 'Description']
def fearnings(time):
    return df.at[time, 'Event'] == 'Earnings'

sieve = valuehunter.sieve.Sieve(lambda time: fbefore(time) or fafter(time), fearnings)
s = set([pair[1] for pair in namespace.values if pair[1] == pair[1]])
pd.DataFrame(s).to_clipboard(index=False, header=False)
print('Copied all filtered tickers to clip-board.')