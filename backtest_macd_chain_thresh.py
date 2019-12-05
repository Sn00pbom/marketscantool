import backtrader as bt
import valuehunter as vh
import strategies
from datetime import datetime, timedelta
import argparse


def run():
    # get args
    args = parse_args()

    def log(msg, force=False):
        if args.verbose or force:
            print('{}\t{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))

    log('Started...', force=True)

    # get summary and earnings data
    try:
        log('Loading summary data...')
        summary_df = vh.data.local.get_dataset_summary()
        log('Loading all earnings data...')
        all_earnings_df = vh.data.local.get_all_earnings()
    except FileNotFoundError as e:
        print(e)
        exit()

    # namespace = summary_df.index
    namespace = args.symbol
    # buffer = StringIO()
    log('Using namespace ' + str(namespace))

    for ticker in namespace:

        log('Ticker @ {}'.format(ticker), force=True)

        try:
            log('Loading...')
            ticker_prices = vh.data.local.get_price_history(ticker)
            log('Loaded!')
        except FileNotFoundError:
            log('FileNotFoundError @ {}\tskipping...'.format(ticker))
            continue

        if ticker not in summary_df.index:
            log('Not in earnings dataset -> skipping...', force=True)
            continue

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
        log('Backtesting {} from {} to {}'.format(ticker, from_date, to_date))

        # init Cerebro
        cerebro = bt.Cerebro()  # create Cerebro object
        # TODO change all_earnings_df to pass only ticker df
        cerebro.addstrategy(strategies.MACDComposite,
                            all_earnings_df=all_earnings_df,
                            delay=args.delay,
                            verbose=args.verbose,
                            ticker=ticker,
                            sl=args.stoptrailpercent,
                            # rr_ratio=
                            max_percent=args.maxthreshpercent,
                            trigger_percent=args.triggerthreshpercent,
                            macd_periods=args.macd,
                            chainlenlookback=args.chainlenlookback,
                            reversal_only=not args.anychain,  # anychain means not reversal only
                            trigger_chainlen=args.triggerchainlen,
                            sim_weights=args.simweights)

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

        # add csv writer to Cerebro
        # cerebro.addwriter(bt.WriterFile, csv=True, out=buffer)

        log('\n\tBeginning Value: {}\n\tBeginning Cash: {}'.format(cerebro.broker.getvalue(), cerebro.broker.getcash()),
            force=True)
        try:
            cerebro.run(max_cpus=4)  # loop over loaded data
        except IndexError:
            print('IndexError @ {} - continuing'.format(ticker))
            continue
        log('\n\tEnding Value: {}\n\tEnding Cash: {}'.format(cerebro.broker.getvalue(), cerebro.broker.getcash()),
            force=True)
        if args.plot:
            cerebro.plot()



def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Backtest a single ticker or multiple tickers with MACDComposite Strategy'
    )

    parser.add_argument('--simweights', '-sw', nargs=4, type=float, default=[1., 1., 1., 1.],
                        metavar=('WO', 'WH', 'WL', 'WC'),
                        help='Define weights to be used for weighted avg price (default: all 1.0)')

    parser.add_argument('--delay', '-d', type=int, default=3,
                        help='Delay between recognized pattern and position entry times (default: 3)')

    parser.add_argument('--macd', '-m', nargs=3, type=int, default=[12, 26, 9],
                        metavar=('PERIOD_SHORT', 'PERIOD_LONG', 'PERIOD_SIGNAL'),
                        help='Define periods to be used in MACD (default: 12 26 9)')

    parser.add_argument('--anychain', '-ac', action='store_true',
                        help='Count MACD histo chain regardless of reversal state')

    parser.add_argument('--chainlenlookback', '-cllb', type=int, default=2,
                        help='MACD Histo chain lookback length L (default: 2)')

    parser.add_argument('--triggerchainlen', '-tcl', type=int, default=10,
                        help='MACD Histo chain length that will trigger condition (default: 10)')

    parser.add_argument('--maxthreshpercent', '-mtp', type=float, default=0.8,
                        metavar='PERCENT',
                        help='MACD max value percent threshold (default: 0.8)')

    parser.add_argument('--triggerthreshpercent', '-ttp', type=float, default=0.8,
                        metavar='PERCENT',
                        help='MACD value percent that will trigger condition (default 0.8)')

    parser.add_argument('--stoptrailpercent', '-s', type=float, default=0.05,
                        metavar='PERCENT',
                        help='Trailing Stop delta percent (default: 0.05)')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable logging small details during back-testing.')

    parser.add_argument('--plot', '-p', action='store_true',
                        help='Enable plotting at the end of each ticker back-test.')

    parser.add_argument('symbol', type=str, nargs='+',
                        help='Stock symbol(s) to back-test.')

    # TODO add data path argument

    return parser.parse_args(pargs)


if __name__ == '__main__':
    run()

