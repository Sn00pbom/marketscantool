from sys import argv
from datetime import datetime

import backtrader as bt

import valuehunter as vh
import feedadapters


class NuStrat(bt.Strategy):
    params = (
            ('stop_percent', None),
            ('limit_percent', None),
            ('macd_periods', [12, 26, 9]),
            )

    def __init__(self):
        macd = bt.indicators.MACDHisto(self.datas[0],
                period_me1=self.p.macd_periods[0],
                period_me2=self.p.macd_periods[1],
                period_signal=self.p.macd_periods[2])
        self.macd_crossup = bt.ind.CrossUp(macd.macd, macd.signal)
        self.macd_crossdown = bt.ind.CrossUp(macd.signal, macd.macd)

        # Track orders
        self.sl_order = None  # stop loss order
        self.lim_order = None  # limit order
        self.tp_order = None  # take profit order

    def next_open(self):
        if not self.position:
            price = self.data.close[0]
            if self.macd_crossdown:
                # Bearish
                self.tp_order = self.sell(transmit=False)
                self.sl_order = self.buy(
                        transmit=False,
                        parent=self.tp_order,
                        exectype=bt.Order.Stop,
                        price=price * (1.0 + self.p.stop_percent),
                        )
                self.lim_order = self.buy(
                        transmit=True,
                        parent=self.tp_order,
                        exectype=bt.Order.Limit,
                        price=price * (1.0 - self.p.limit_percent),
                        )
            elif self.macd_crossup:
                # Bullish
                self.tp_order = self.buy(transmit=False)
                self.sl_order = self.sell(
                        transmit=False,
                        parent=self.tp_order,
                        exectype=bt.Order.Stop,
                        price=price * (1.0 - self.p.stop_percent),
                        )
                self.lim_order = self.sell(
                        transmit=True,
                        parent=self.tp_order,
                        exectype=bt.Order.Limit,
                        price=price * (1.0 + self.p.limit_percent),
                        )

        else:
            # Just wait for stop/limit
            pass


if __name__ == "__main__":
    if len(argv) != 4:
        print('USAGE: nustrat.py [STOP %] [LIMIT %] [PATH]')
        exit(1)

    STAKE = 1
    EQUITY = 100000
    COMMISSION = 0.000
    _, stop_percent, limit_percent, PATH = argv
    stop_percent = float(stop_percent)
    limit_percent = float(limit_percent)

    cerebro = bt.Cerebro(cheat_on_open=True)
    cerebro.addstrategy(NuStrat, stop_percent=stop_percent, limit_percent=limit_percent)
    # data_feed = bt.feeds.YahooFinanceCSVData(dataname=PATH)
    data_feed = feedadapters.BarchartCSVData(dataname=PATH)
    cerebro.adddata(data_feed)
    cerebro.addsizer(bt.sizers.FixedSize, stake=STAKE)  # set fixed sizer
    cerebro.broker.set_cash(EQUITY)  # set initial equity
    cerebro.broker.setcommission(commission=COMMISSION)  # set broker commission to .1%

    cerebro.addwriter(bt.WriterFile, csv=True, out='summary_{}.csv'.format(datetime.now().strftime('%H%M%S')))

    cerebro.run(max_cpus=4)
    cerebro.plot()

