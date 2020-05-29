from sys import argv

import backtrader as bt

import valuehunter as vh


class NuStrat():
    params = (
            ('stop_percent', None),
            ('limit_percent', None),
            ('macd_periods', [12, 26, 9]),
            )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.macd_histo = bt.indicators.MACDHisto(self.datas[0],
                period_me1=self.p.macd_periods[0],
                period_me2=self.p.macd_periods[1],
                period_signal=self.p.macd_periods[2])

        # Track orders
        self.sl_order = None  # stop loss order
        self.lim_order = None  # limit order
        self.tp_order = None  # take profit order

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

    def next_open(self):
        if not self.position:
            if self.macd_histo[0] > 0 and self.macd_histo[-1] < 0:
                self.tp_order = self.sell()
                self.sl_order = self.buy(exectype=bt.Order.Stop,

                        parent=self.tp_order)
                self.lim_order = self.buy(price=self.sim[0] * (1.0 - self.p.limit_percent),
                        exectype=bt.Order.Limit,
                        transmit=True, parent=self.tp_order)
            elif self.macd_histo[0] < 0 and self.macd_histo[-1] > 0:
                cross = 'short'

        else:
            # Just wait for stop/limit
            pass


if __name__ == "__main__":
    if len(argv) != 3:
        print('USAGE: nustrat.py [STOP %] [LIMIT %]')
        exit(1)

    PATH = "~/Downloads/NQ=F.csv"
    STAKE = 100
    EQUITY = 100000
    COMMISSION = 0.001
    _, stop_percent, limit_percent = argv

    cerebro = bt.Cerebro(cheat_on_open=True)
    cerebro.addstrategy(NuStrat, stop_percent=stop_percent, limit_percent=limit_percent)
    data_feed = bt.feeds.YahooFinanceCSVData(dataname=PATH)
    cerebro.adddata(data_feed)
    cerebro.addsizer(bt.sizers.FixedSize, stake=STAKE)  # set fixed sizer
    cerebro.broker.set_cash(EQUITY)  # set initial equity
    cerebro.broker.setcommission(commission=COMMISSION)  # set broker commission to .1%

