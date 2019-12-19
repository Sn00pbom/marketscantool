import random

from backtesting import Backtest, Strategy
from finta import TA
import pandas as pd
from pandas import DataFrame

import valuehunter as vh


class MacdChain(Strategy):
    AMP_THRESH_PERCENT = .5

    def init(self):
        # computations here
        self.earn = self.I(lambda: edf, name='hasEarnings')

        close_df = self.data.Close.to_series().rename('close')
        self.macd = TA.MACD(DataFrame(close_df))
        self.hi_amp_thresh = vh.grade.macd.hi_thresh_macd(self.macd, self.AMP_THRESH_PERCENT)
        self.lo_amp_thresh = vh.grade.macd.lo_thresh_macd(self.macd, self.AMP_THRESH_PERCENT)
        self.hist = self.macd['SIGNAL'] - self.macd['MACD']
        self.macd = self.I(lambda: self.macd, name='MACD')
        self.chain_len = self.I(self.rolling_macd_chain, self.hist, 25, name='MACD Chain')
        self.mid = self.I(lambda price_open, price_close: (price_open + price_close)/2,
                          self.data.Open, self.data.Close, name='Mid')
        self.peak = 0.0
        self.ts = 0.0
        self.ts_percent = 0.05
        self.L1 = 2  # wait time to enter position after pattern find
        self.L2 = 1  # wait time to exit position after entry
        self.patterns = []

    def next(self):

        if self.earn:  # is earnings date
            self.patterns = []  # reset all tracked patterns on earnings dates
            self.orders.cancel()

        else:
            for pattern in self.patterns:  # increment all pattern l1
                pattern[1] += 1

            if self.position:  # in a position

                # trailing stop logic

                if self.position.is_long:  # long position

                    if self.mid[-1] <= self.ts:
                        self.position.close()

                    if self.mid[-1] > self.peak:
                        self.peak = self.mid[-1]
                    self.ts = self.mid[-1] - self.peak * self.ts_percent

                else:  # short position

                    if self.mid[-1] >= self.ts:
                        self.position.close()

                    if self.mid[-1] < self.peak:
                        self.peak = self.mid[-1]
                    self.ts = self.mid[-1] + self.peak * self.ts_percent

            else:  # not in a position

                # TODO change to weighted score check
                # check for enter conditions
                if self.chain_len >= 10 and self.macd[-1] >= self.hi_amp_thresh:
                    self.patterns.append(['bear', 0, 0])  # track bearish pattern

                elif self.chain_len <= -10 and self.macd[-1] <= self.lo_amp_thresh:
                    self.patterns.append(['bull', 0, 0])  # track bullish pattern

                ris = []  # indices to remove
                for i, pattern in enumerate(self.patterns):
                    p, l1, l2 = pattern
                    if l1 == self.L1:
                        ris.append(i)

                        if p == 'bear':
                            self.sell(price=self.mid)

                            # compute trailing stop
                            self.peak = self.mid
                            self.ts = self.mid + self.peak * self.ts_percent
                            break
                        elif p == 'bull':
                            self.buy(price=self.mid)

                            # compute trailing stop
                            self.peak = self.mid
                            self.ts = self.mid - self.peak * self.ts_percent
                            break

                self.patterns = [self.patterns[i] for i in range(len(self.patterns)) if i not in ris]

    @staticmethod
    def rolling_macd_chain(macd, period):
        return macd.rolling(period).apply(lambda vals: vh.grade.macd.histogram_chain(vals, look_back=1, reversal=True) * -1)
    

ns_path = "C:/dataset/amex-nyse-nasdaq-stock-histories/fh_20190420/NASDAQ.txt"
namespace = vh.data.local.namespace_from_tab_delimited(ns_path)
earnings_df = vh.data.local.get_all_earnings()
earn_summary = vh.data.local.get_dataset_summary()
earnings_df = vh.data.compat.set_datetime_index(earnings_df)

everything = []
for ticker in namespace:
    print('computing',ticker)

    try:
        df = vh.data.local.get_price_history(ticker)
    except FileNotFoundError as e:
        print('NO DATA @', ticker)
        continue
    df = vh.data.compat.format_df_backtest(df)
    earn = vh.data.local.get_ticker_earnings(earnings_df, ticker)

    edf = DataFrame(df.index.isin(earn.index, level='date'), index=df.index)
    edf = edf.iloc[::-1]
    bt = Backtest(df, MacdChain,
                  cash=10000, commission=.002)
    results = bt.run()
    bt.plot()
    results['Symbol'] = ticker
    everything.append(results)

everything = pd.DataFrame(everything)
print(everything)
