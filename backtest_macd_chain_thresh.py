import backtrader as bt
import valuehunter as vh
import pandas as pd
import datetime
import strategies
from datetime import datetime, timedelta


if __name__ == '__main__':

    ticker = 'ROKU'

    # get earnings calendar from and to dates
    summary_df = vh.data.local.get_dataset_summary()
    form = '%Y-%m-%d'
    delta = timedelta(days=40)
    from_date = datetime.strptime(summary_df.at[ticker, 'earnings_from_date'], form) - delta
    to_date = datetime.strptime(summary_df.at[ticker, 'earnings_to_date'], form) + delta
    print('Earnings Data From:', from_date)
    print('Earnings Data To:', to_date)

    # init Cerebro
    cerebro = bt.Cerebro()  # create Cerebro object
    cerebro.addstrategy(strategies.MACDComposite,
                        Lc=10, L1=0, min_grade=80.0, printlog=True, ticker=ticker,
                        all_earnings_df=vh.data.local.get_all_earnings())

    # create DataFeed and add to cerebro
    data_feed = bt.feeds.YahooFinanceCSVData(
        dataname='./dat/yahoo_AAPL_5y1d.csv',
        # Do not pass values before this date
        # fromdate=datetime.datetime(2016, 1, 1),
        fromdate=from_date,
        # Do not pass values after this date
        todate=to_date,
        # therefore, domain is [start, end)
        reverse=False)
    cerebro.adddata(data_feed)


    cerebro.addsizer(bt.sizers.FixedSize, stake=1)  # set fixed sizer

    cerebro.broker.set_cash(10000.0)  # set initial equity to $10k
    cerebro.broker.setcommission(commission=0.001)  # set broker commission to .1%

    print(cerebro.broker.getvalue())
    print(cerebro.broker.getcash())
    cerebro.run(max_cpus=4)  # loop over loaded data
    print(cerebro.broker.getvalue())
    print(cerebro.broker.getcash())
    cerebro.plot()

