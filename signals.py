import backtrader as bt
import valuehunter as vh
from pandas import DataFrame


class SimPrice(bt.Indicator):
    lines = ('trade_price',)
    params = (
        ('w_o', 1),
        ('w_h', 1),
        ('w_l', 1),
        ('w_c', 1),
    )

    def __init__(self):
        w = [self.p.w_o, self.p.w_h, self.p.w_l, self.p.w_c]
        d = [self.data.open, self.data.high, self.data.low, self.data.close]
        self.lines.trade_price = sum(w * d for w, d in zip(w, d))/sum(w)


class MACDHistoChain(bt.Indicator):
    lines = ('chain_len',)
    params = (
        ('period_me1', 12),
        ('period_me2', 26),
        ('period_signal', 9),
        ('movav', bt.indicators.ExponentialMovingAverage),
        ('L', 2),
        ('rev', True),
    )

    def __init__(self):
        macd = bt.indicators.MACDHisto(
            period_me1=self.p.period_me1,
            period_me2=self.p.period_me2,
            period_signal=self.p.period_signal,
            movav=self.p.movav
        )
        self.histo = macd.histo

    def next(self):
        d = self.histo.get(size=50).tolist()
        if len(d) == 0:
            self.lines.chain_len[0] = 0
        else:
            chain = vh.grade.macd.histogram_chain(d, self.p.L, self.p.rev)
            self.lines.chain_len[0] = chain


class Earnings(bt.Indicator):
    lines = ('has_earnings',)
    params = (
        ('ticker', None),
        ('all_earnings_df', None),
    )

    def __init__(self):
        if self.p.ticker is None:
            raise ValueError('Missing ticker name.')

        if self.p.all_earnings_df is None:
            raise ValueError('Missing earnings DataFrame.')

        self.earnings = vh.data.local.get_ticker_earnings(self.p.ticker, self.p.all_earnings_df)
        self.earnings = self.earnings['date'].tolist()

    def next(self):
        today_earnings = str(self.data.datetime.date()) in self.earnings
        self.lines.has_earnings[0] = today_earnings
