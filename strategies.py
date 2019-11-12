from valuehunter.strategy import Strategy
from valuehunter.strategy import decision

class MACDReversalChainLength(Strategy):
    @staticmethod
    def predict(ticker_df):
        return decision.BUY_LONG
