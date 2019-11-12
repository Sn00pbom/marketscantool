
class Backtester(object):
    def __init__(self, market_df):
        self._df = market_df # market dataframe for one ticker
        self._itoday = 0 # second to last value if 'tomorrow' is first
        self._outcome_history = []

    def _next_memory(self):
        # TODO test
        n = self._df.iloc[:-1 - self._itoday]
        self._itoday += 1
        return n

    def _test_memory(self):
        # TODO implement
        pass

    def backtest(self):
        # TODO implement
        pass

