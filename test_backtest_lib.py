from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import valuehunter as vh
from backtesting.test import SMA, GOOG
from finta import TA
from yahoo_finance_api2 import share
from pandas import DataFrame
import numpy as np

class SmaCross(Strategy):
    def init(self):
        Close = self.data.Close
        self.ma1 = self.I(SMA, Close, 10)
        self.ma2 = self.I(SMA, Close, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


class MacdChain(Strategy):

    def init(self):
        # computations here
        close_df = self.data.Close.to_series().rename('close')
        self.macd = TA.MACD(DataFrame(close_df))
        self.hist = self.macd['SIGNAL'] - self.macd['MACD']
        self.macd = self.I(TA.MACD, DataFrame(self.data.Close.to_series()).rename(columns={'Close':'close'}))
        self.chain_len = self.I(self.rolling_macd_chain, self.hist, 25)
        self.n_days=0
        
    def next(self):
        # buy/sell condition here
        if not self.position:
            if self.chain_len >= 10:
                self.sell()
            elif self.chain_len <= -10:
                self.buy()
        else:
            if self.n_days == 3:
                self.position.close()
                self.n_days = 0
            else:
                self.n_days += 1
            # if self.position.is_long:
            #     self.position.close()
            # elif self.position.is_short:
            #     self.position.close()

    @staticmethod
    def rolling_macd_chain(macd, period):
        return macd.rolling(period).apply(lambda vals: vh.grade.macd.histogram_chain(vals, L=2, reversal=True) * -1)

        
namespace = vh.data.namespace.from_tos_wl('./dat/wl.csv')
everything = []
for ticker in namespace:

    df = vh.data.yahoo.get_historical_data(ticker, share.PERIOD_TYPE_YEAR, 1, share.FREQUENCY_TYPE_DAY, 1, standardize=True) # load 'ROKU' data
    if df is None or df.empty: continue
    df = df.drop(columns='timestamp') # drop timestamp
    # df.set_index('timestamp')
    df = df.rename(columns={key:key.capitalize() for key in df}) # capitalize all column names
    bt = Backtest(df, MacdChain,
                cash=10000, commission=.002)
                
    results = bt.run()
    bt.plot()

    everything.append(results['Win Rate [%]'])
everything = [x for x in everything if str(x) != 'nan']
print(sum(everything)/len(everything))
# bt.plot()