import backtrader as bt
import valuehunter as vh
import pandas as pd
import datetime
import strategies
from datetime import datetime, timedelta
from io import StringIO


if __name__ == '__main__':

    # get earnings calendar from and to dates
    summary_df = vh.data.local.get_dataset_summary()
    all_earnings_df = vh.data.local.get_all_earnings()
    # all_prices_df = vh.data.local.get_all_prices()
    # all_prices_df = pd.read_csv('./dat/all_prices_mini.csv', parse_dates=['date'])  # parse dates in column 1 'date'


    # namespace = summary_df.index
    namespace = ['ROKU', 'AAPL', 'GHSI', 'FLIC', 'IMUX', 'AMD', 'AMZN']

    for ticker in namespace:
        print(ticker)

        # get ticker dataframe
        try:
            ticker_prices = vh.data.local.get_price_history(ticker)
        except FileNotFoundError:
            print('fnf')
            continue

        # if ticker_prices.shape[0] < 50:
        #     continue
        ticker_prices = ticker_prices.sort_values(by='date')
        ticker_prices = ticker_prices.set_index(['date'])

        # get earnings dates
        form = '%Y-%m-%d'
        delta = timedelta(days=40)
        from_s = summary_df.at[ticker, 'earnings_from_date']
        from_s = from_s if isinstance(from_s, str) else summary_df.at[ticker, 'stock_from_date']
        to_s = summary_df.at[ticker, 'earnings_to_date']
        to_s = to_s if isinstance(to_s, str) else summary_df.at[ticker, 'stock_to_date']
        from_date = datetime.strptime(from_s, form) - delta
        to_date = datetime.strptime(to_s, form) + delta
        print('Earnings Data From:', from_date)
        print('Earnings Data To:', to_date)

        # init Cerebro
        cerebro = bt.Cerebro()  # create Cerebro object
        cerebro.addstrategy(strategies.MACDComposite,
                            Lc=10, L1=2, min_grade=80.0, printlog=True, ticker=ticker,
                            all_earnings_df=all_earnings_df)

        # send dataframe to DataFeed
        data_feed = bt.feeds.PandasData(
            dataname=ticker_prices,
            fromdate=from_date,
            todate=to_date,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
        )
        cerebro.adddata(data_feed)

        cerebro.addsizer(bt.sizers.FixedSize, stake=10)  # set fixed sizer

        cerebro.broker.set_cash(10000.0)  # set initial equity to $10k
        cerebro.broker.setcommission(commission=0.001)  # set broker commission to .1%

        print('Beginning Value: {}\nBeginning Price: {}'.format(cerebro.broker.getvalue(), cerebro.broker.getcash()))
        try:
            cerebro.run(max_cpus=4)  # loop over loaded data
        except IndexError:
            print('IndexError @ {} - continuing'.format(ticker))
            continue
        print('Ending Value: {}\nEnding Price: {}'.format(cerebro.broker.getvalue(), cerebro.broker.getcash()))
        cerebro.plot()

