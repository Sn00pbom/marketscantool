import sys

from pandas import DataFrame

import valuehunter


def filter_calendar(calendar_path: str, after_date: str, before_date: str):
    calendar_df = valuehunter.data.think_or_swim.to_dataframe(calendar_path)
    calendar_df = calendar_df.set_index('Symbol')
    namespace = list(calendar_df.index)
    sieve = valuehunter.sieve.Sieve(lambda ticker:
                                    (calendar_df.at[ticker, 'Time est'] == 'After Market'
                                        and calendar_df.at[ticker, 'Date est'] == after_date)
                                    or
                                    (calendar_df.at[ticker, 'Time est'] == 'Before Market'
                                        and calendar_df.at[ticker, 'Date est'] == before_date))
    return DataFrame(sieve.sift(namespace))


if __name__ == '__main__':
    if not len(sys.argv) is 4:
        print('python filter_calendar.py [CALENDAR PATH] [AFTER DATE] [BEFORE DATE]\n'
              'Dates will be one character if single digit.')
        exit()
    path = sys.argv[1]
    after_s = sys.argv[2]
    before_s = sys.argv[3]
    df = filter_calendar(path, after_s, before_s)
    print(df)

    df.to_clipboard(index=False, header=False)
    print('Copied all filtered tickers to clip-board.')
