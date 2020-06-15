import backtrader as bt

import valuehunter as vh


class SimPrice(bt.Indicator):
    lines = ('trade_price',)
    params = (
        ('weights', [1.0, 1.0, 1.0, 1.0]),  # [o, h, l, c]
    )

    def __init__(self):
        w = self.p.weights
        d = [self.data.open, self.data.high, self.data.low, self.data.close]
        self.lines.trade_price = sum(w * d for w, d in zip(w, d))/sum(w)


class MACDHistoChain(bt.Indicator):
    lines = ('chain_len',)
    params = (
        ('macd_periods', [12, 26, 9]),
        ('L', 2),
        ('reversal_only', True),
    )

    def __init__(self):

        macd = bt.indicators.MACDHisto(
            period_me1=self.p.macd_periods[0],
            period_me2=self.p.macd_periods[1],
            period_signal=self.p.macd_periods[2],
        )
        self.histo = macd.histo

    def next(self):
        d = self.histo.get(size=50).tolist()
        if len(d) == 0:
            self.lines.chain_len[0] = 0
        else:
            chain = vh.grade.macd.histogram_chain(d, self.p.L, self.p.reversal_only)
            self.lines.chain_len[0] = chain


class Earnings(bt.Indicator):
    lines = ('has_earnings',)
    params = (
        ('ticker', None),
        ('earnings_df', None),
    )

    def __init__(self):
        if self.p.ticker is None:
            raise ValueError('Missing ticker name.')

        if self.p.earnings_df is None:
            raise ValueError('Missing earnings DataFrame.')

        self.earnings = self.p.earnings_df
        self.earnings = self.earnings['date'].tolist()

    def next(self):
        today_earnings = str(self.data.datetime.date()) in self.earnings
        self.lines.has_earnings[0] = today_earnings

class Threshold(bt.Indicator):
    lines = ('hi_thresh', 'lo_thresh', 'hi_exceed', 'lo_exceed', 'indicator',)
    params = (
        ('trigger_percent', .8),
        ('mem_max', 50), # max number of periods held in threshold memory (-1 for no maximum)
        ('indicator', None),
    )

    def __init__(self):
        self.lines.indicator = self.p.indicator
        self.mem = list()

    def next(self):
        self.mem.append(self.lines.indicator[0])
        if self.p.mem_max >= 0 and len(self.mem) > self.p.mem_max:
            self.mem.pop(0)

        # compute hi signals
        hi_thresh_i = max(self.mem)
        self.lines.hi_thresh[0] = hi_thresh_i
        self.lines.hi_exceed[0] = (self.indicator[0]/hi_thresh_i if hi_thresh_i else self.p.trigger_percent+1) > self.p.trigger_percent
        
        # compute lo signals
        lo_thresh_i = min(self.mem)
        self.lines.lo_thresh[0] = lo_thresh_i
        self.lines.lo_exceed[0] = (self.indicator[0]/lo_thresh_i if lo_thresh_i else self.p.trigger_percent+1) > self.p.trigger_percent

class MACDThresholdPercent(Threshold):
    params = (
        ('macd_periods', [12, 26, 9]),
    )

    def __init__(self):
        macd = bt.indicators.MACDHisto(
            period_me1=self.p.macd_periods[0],
            period_me2=self.p.macd_periods[1],
            period_signal=self.p.macd_periods[2],
        )
        self.p.indicator = macd.macd
        super().__init__()
