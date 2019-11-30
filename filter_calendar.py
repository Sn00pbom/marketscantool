import sys
import valuehunter
from pandas import DataFrame


def filter_calendar(path, after_date: str, before_date: str):
    df = valuehunter.data.think_or_swim.to_dataframe(path)
    df = df.set_index('Symbol')
    namespace = list(df.index)
    sieve = valuehunter.sieve.Sieve(lambda ticker:
                                    (df.at[ticker, 'Time est'] == 'After Market'
                                        and df.at[ticker, 'Date est'] == after_date)
                                    or
                                    (df.at[ticker, 'Time est'] == 'Before Market'
                                        and df.at[ticker, 'Date est'] == before_date))
    return DataFrame(sieve.sift(namespace))


if __name__ == '__main__':
    if not len(sys.argv) is 4:
        print('python filter_calendar.py [CALENDAR PATH] [AFTER DATE] [BEFORE DATE]\nDates will be one character if single digit.')
        exit()
    path = sys.argv[1]
    after_s = sys.argv[2]
    before_s = sys.argv[3]
    df = filter_calendar(path, after_s, before_s)
    print(df)

    df.to_clipboard(index=False, header=False)
    print('Copied all filtered tickers to clip-board.')
