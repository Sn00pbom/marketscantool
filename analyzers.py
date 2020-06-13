from io import StringIO
from datetime import datetime as dt
import backtrader as bt
from backtrader import Analyzer


class AdjacentPositionSummary(Analyzer):
    params = (
            ('headers', ['isbuy', 'issell', 'price', 'pnl', 'tot pnl']),
            )

    def __init__(self):
        super(AdjacentPositionSummary, self).__init__()
        self._o = StringIO()
        print(*self.p.headers, sep=',', file=self._o)
        self._tot_pnl = 0

    def notify_order(self, order):
        if order.status == order.Completed:
            # print(dt.fromtimestamp(order.executed.dt), order.isbuy(), order.issell(), order.executed.price, sep=',', file=self._o)
            self._tot_pnl += order.executed.pnl
            print(order.isbuy(), order.issell(), order.executed.price, order.executed.pnl, self._tot_pnl, sep=',', file=self._o)

    def get_analysis(self):
        return self._o.getvalue()

