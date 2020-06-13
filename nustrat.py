from sys import argv
from datetime import datetime

import backtrader as bt

import valuehunter as vh
import feedadapters
import analyzers


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

    def next(self):
        if not self.position:
            close = self.data.close[0]
            if self.macd_crossdown:
                # Bearish
                orders = self.sell_bracket(
                        limitprice=close*(1.0 - self.p.limit_percent),
                        stopprice=close*(1.0 + self.p.stop_percent),
                        )
            elif self.macd_crossup:
                # Bullish
                orders = self.buy_bracket(
                        limitprice=close*(1.0 + self.p.limit_percent),
                        stopprice=close*(1.0 - self.p.stop_percent),
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

    cerebro = bt.Cerebro()
    cerebro.addstrategy(NuStrat, stop_percent=stop_percent, limit_percent=limit_percent)
    # data_feed = bt.feeds.YahooFinanceCSVData(dataname=PATH)
    data_feed = feedadapters.BarchartCSVData(dataname=PATH)
    cerebro.adddata(data_feed)
    cerebro.addsizer(bt.sizers.FixedSize, stake=STAKE)  # set fixed sizer
    cerebro.broker.set_cash(EQUITY)  # set initial equity
    cerebro.broker.setcommission(commission=COMMISSION)  # set broker commission

    cerebro.addanalyzer(analyzers.AdjacentPositionSummary, _name='aps')
    results = cerebro.run(max_cpus=4)
    cerebro.plot()

    out_path = 'summary_{}.csv'.format(datetime.now().strftime('%H%M%S'))
    with open(out_path, 'w') as f:
        f.write(results[0].analyzers.aps.get_analysis())
