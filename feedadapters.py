import itertools
from datetime import datetime
from io import StringIO

import backtrader as bt

class BarchartCSVData(bt.feeds.GenericCSVData):
    params = (
            ('dtformat', ('%Y-%m-%dT%H:%M:%S-05:00')),
            ('datetime', 1),
            ('open', 3),
            ('high', 4),
            ('low', 5),
            ('close', 6),
            ('volume', 7),
            )

    def _loadline(self, tokens):
        tokens = [token.replace('"', '') for token in tokens]
        dt = datetime.strptime(tokens[self.p.datetime],
                self.p.dtformat)
        self.lines.datetime[0] = self.date2num(dt)
        self.lines.open[0] = float(tokens[self.p.open])
        self.lines.high[0] = float(tokens[self.p.high])
        self.lines.low[0] = float(tokens[self.p.low])
        self.lines.close[0] = float(tokens[self.p.close])
        self.lines.volume[0] = float(tokens[self.p.volume])
        return True

