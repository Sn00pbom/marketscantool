from backtesting import Backtest, Strategy
import valuehunter as vh
from finta import TA
from pandas import DataFrame
import random
import pandas as pd

# from backtesting.lib import crossover, TrailingStrategy
# from yahoo_finance_api2 import share
# import numpy as np
# from backtesting.test import SMA, GOOG
# class SmaCross(Strategy):
#     def init(self):
#         Close = self.data.Close
#         self.ma1 = self.I(SMA, Close, 10)
#         self.ma2 = self.I(SMA, Close, 20)

#     def next(self):
#         if crossover(self.ma1, self.ma2):
#             self.buy()
#         elif crossover(self.ma2, self.ma1):
#             self.sell()

# TODO memory replay
# def __bool__(self) return boolean when instance checked

class MacdChain(Strategy):

    def init(self):
        # computations here
        global edf
        # print(edf[edf[0] == True])
        self.earn = self.I(lambda: edf, name='hasEarnings')

        close_df = self.data.Close.to_series().rename('close')
        self.macd = TA.MACD(DataFrame(close_df))
        AMP_THRESH_PERCENT = .5
        self.hi_amp_thresh = vh.grade.macd.hi_thresh_macd(self.macd, AMP_THRESH_PERCENT)
        self.lo_amp_thresh = vh.grade.macd.lo_thresh_macd(self.macd, AMP_THRESH_PERCENT)
        self.hist = self.macd['SIGNAL'] - self.macd['MACD']
        # self.macd = self.I(TA.MACD, DataFrame(self.data.Close.to_series()).rename(columns={'Close': 'close'}))
        self.macd = self.I(lambda: self.macd, name='MACD')
        self.chain_len = self.I(self.rolling_macd_chain, self.hist, 25, name='MACD Chain')
        self.mid = self.I(lambda price_open, price_close: (price_open + price_close)/2,
                          self.data.Open, self.data.Close, name='Mid')
        self.peak = 0.0
        self.ts = 0.0
        self.ts_percent = 0.05
        # self.last_mid = 0.0
        self.L1 = 2  # wait time to enter position after pattern find
        self.L2 = 1  # wait time to exit position after entry
        self.patterns = []

    def next(self):

        if self.earn:  # is earnings date
            self.patterns = []  # reset all tracked patterns on earnings dates
            # self.position.close()
            self.orders.cancel()

        else:
            for pattern in self.patterns:  # increment all pattern l1
                # p, l1, l2 = pattern
                # l1 += 1
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



        # buy/sell condition here
        # if not self.position and not self.earn:
        #     if self.chain_len >= 10:
        #         self.sell(self.mid)
        #     elif self.chain_len <= -10:
        #         self.buy(self.mid)
        # else:
        #     self.position.close()
        #     self.n_days = 0


    @staticmethod
    def rolling_macd_chain(macd, period, raw=True):
        return macd.rolling(period).apply(lambda vals: vh.grade.macd.histogram_chain(vals, L=1, reversal=True) * -1)
    

# namespace = vh.data.local.namespace_from_symbol_list('./namespace.txt')
ns_path = "C:/dataset/amex-nyse-nasdaq-stock-histories/fh_20190420/NASDAQ.txt"
namespace = vh.data.local.namespace_from_tab_delimited(ns_path)
# namespace = vh.data.think_or_swim.watchlist_to_namespace('./dat/small_wl.csv')
earnings_df = vh.data.local.get_all_earnings()
earn_summary = vh.data.local.get_all_earnings_summary()
earnings_df = vh.data.compat.set_datetime_index(earnings_df)
# namespace = vh.data.local.namespace_from_summary(earn_summary)

# print(len(namespace))
# exit()

quantity = 500
ri = [random.randrange(0,len(namespace)) for _ in range(quantity)]
print(ri)
namespace = [name for i, name in enumerate(namespace) if i in ri]
namespace = ['ASYS']
everything = []
for ticker in namespace:
    print('computing',ticker)

    # df = vh.data.yahoo.get_historical_data(ticker, share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_DAY, 1, standardize=True) # load 'ROKU' data
    try:
        df = vh.data.local.get_historical_daily(ticker)
    except FileNotFoundError as e:
        print('NO DATA @', ticker)
        continue
    df = vh.data.compat.format_df_backtest(df)
    earn = vh.data.local.get_ticker_earnings(earnings_df, ticker)

    # try:
    edf = DataFrame(df.index.isin(earn.index, level='date'), index=df.index)
    edf = edf.iloc[::-1]
    # print(edf)
    bt = Backtest(df, MacdChain,
                cash=10000, commission=.002)
    results = bt.run()
    bt.plot()
    # everything.append(results['Win Rate [%]'])
    results['Symbol'] = ticker
    everything.append(results)
    # except:
    #     print('ERROR @', ticker)
    #     continue

# everything = [x for x in everything if str(x) != 'nan']
everything = pd.DataFrame(everything)
# print(sum(everything)/len(everything))
print(everything)
# everything.to_csv('./dat/backtest-out.csv')
