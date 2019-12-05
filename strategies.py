import valuehunter as vh
import backtrader as bt
import signals


class MACDComposite(bt.Strategy):

    params = (
        ('all_earnings_df', None),
        ('delay', 3),
        ('verbose', True),
        ('ticker', None),
        ('sl', 0.05),
        ('rr_ratio', 3),
        ('max_percent', 0.8),
        ('trigger_percent', 0.8),
        ('macd_periods', [12, 26, 9]),
        ('chainlenlookback', 2),
        ('reversal_only', True),
        ('trigger_chainlen', 10),
        ('sim_weights', [1., 1., 1., 1.]),
    )

    def log(self, txt, dt=None, force=False):
        """Logging function fot this strategy"""
        if self.params.verbose or force:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.price_data = self.datas[0]
        # self.mid = (((price_data.high + price_data.low)/2.) + ((price_data.open + price_data.close)/2.))/2.
        self.macd_histo = bt.indicators.MACDHisto(self.datas[0],
                                                  period_me1=self.p.macd_periods[0],
                                                  period_me2=self.p.macd_periods[1],
                                                  period_signal=self.p.macd_periods[2])
        self.macd_histo_chain = signals.MACDHistoChain(self.datas[0],
                                                       macd_periods=self.p.macd_periods,
                                                       L=self.p.chainlenlookback,
                                                       reversal_only=self.p.reversal_only)
        self.sim = signals.SimPrice(self.datas[0], weights=self.p.sim_weights)
        self.data_close = self.datas[0].close
        self.earnings = signals.Earnings(ticker=self.p.ticker, all_earnings_df=self.p.all_earnings_df)
        self.thresh = signals.MACDThresholdPercent(macd_periods=self.p.macd_periods,
                                                   max_percent=self.p.max_percent,
                                                   trigger_percent=self.p.trigger_percent)

        self.sl_order, self.tp_order = None, None  # track trade profit and stop loss orders
        self.decision = None
        self.l1 = -1
        self.l2 = -1

    def notify_order(self, order):
        # self.log('{} {} {}'.format(order.exectype, order.status, order.tradeid))
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            self.sl_order = None  # stop tracking stop loss if present
            self.l1 = -1  # reset enter position delay counter
            if order.isbuy():  # Buy
                self.log('BUY EXECUTED')

            else:  # Sell
                self.log('SELL EXECUTED')

            # if order.exectype == bt.Order.StopTrail:
            #     print('completed:\n{}'.format(order))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.sl_order = None  # stop tracking stop loss if present
            self.log('Canceled stop loss')
            self.log('Order Canceled/Margin/Rejected')

        self.tp_order = None  # track no pending order

    def notify_trade(self, trade):
        # clear order vars if closed so not in position state
        if trade.isclosed:
            # self.log('Trade closed with value {}'.format(trade.value))  # TODO fix
            pass
            # if trade is not self.sl_order:
            #     self.cancel(self.sl_order)
            # self.sl_order = None
            # self.tp_order = None

    def next(self):

        is_earnings_nearby = False  # earnings announcement withing the next 2 days from 'today'

        try:
            if self.earnings[0]:
                is_earnings_nearby = True
            elif self.earnings[1]:
                is_earnings_nearby = True
            elif self.earnings[2]:
                is_earnings_nearby = True
        except IndexError:
            pass

        if not self.position:
            if self.l1 == -1:
                if not is_earnings_nearby and abs(self.macd_histo_chain[0]) > self.p.trigger_chainlen:
                    if self.macd_histo_chain[0] < 0 and self.thresh.lo_exceed:
                        self.log('Long Pattern Found')
                        self.decision = 'long'
                        self.l1 = 0
                    elif self.macd_histo_chain[0] > 0 and self.thresh.hi_exceed:
                        self.log('Short Pattern Found')
                        self.decision = 'short'
                        self.l1 = 0
            else:
                self.l1 += 1

            if self.l1 == self.p.delay:
                if self.decision == 'long':
                    self.tp_order = self.buy(price=self.sim[0])
                elif self.decision == 'short':
                    self.tp_order = self.sell(price=self.sim[0])

        else:

            if is_earnings_nearby:
                self.log('EARNINGS - DUMPING')
                if self.sl_order:
                    self.broker.cancel(self.sl_order)

                if self.decision == 'long':
                    self.tp_order = self.sell(price=self.sim[0])
                elif self.decision == 'short':
                    self.tp_order = self.buy(price=self.sim[0])

            else:
                if not self.sl_order:  # no stop loss order
                    if self.decision == 'long':
                        self.sl_order = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.p.sl)
                    elif self.decision == 'short':
                        self.sl_order = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.p.sl)


