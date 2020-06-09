import itertools
import datetime as dt

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

