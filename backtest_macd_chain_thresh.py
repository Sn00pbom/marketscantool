import argparse
from datetime import datetime, timedelta

import backtrader as bt

import valuehunter as vh
import strategies


def run(pargs=None):

    # Get args
    args = parse_args(pargs)

    def log(*msg, force=False):
        if args.verbose or force:
            print('{}\t'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), *msg)

    log('Initializing...', force=True)

    # Load earnings dataset
    log('Loading earnings dataset...', force=True)
    try:
        log('Loading summary data...', force=True)
        summary_df = vh.data.local.get_dataset_summary()
        log('Loading earnings data...', force=True)
        all_earnings_df = vh.data.local.get_all_earnings()
    except FileNotFoundError:
        print('No Earnings Dataset. Quitting...')
        exit()

    # Load namespace target from args
    ns_args = []
    if args.namespace:
        optype, ns_path = args.namespace
        log('Namespace file specified: ignoring symbols args', force=True)
        if optype == 'tos':
            ns_args = vh.data.think_or_swim.watchlist_to_namespace(ns_path)
        elif optype == 'nl':
            ns_args = vh.data.local.namespace_from_symbol_list(ns_path)
        else:
            print('Unrecognized type. Quitting...')
            exit()
    else:
        if len(args.symbol) == 0:
            print('Must have symbols or namespace\npython backtest_macd_thresh_chain.py --help')
            exit()
        else:
            ns_args = [str(symbol).upper() for symbol in args.symbol]  # all entered values to upper

    # Symbols in earnings dates and summary data set
    log('Checking symbols in earnings dataset...', force=True)
    ns_earnset = []
    for symbol in ns_args:
        if symbol in summary_df.index:
            ns_earnset.append(symbol)
        else:
            log('Symbol {} not found in Earnings Dataset'.format(symbol), force=True)

    # Symbols in price data set / load datas
    log('Checking and cleaning symbols in price dataset...', force=True)
    prices_dict = {}
    for symbol in ns_earnset:
        try:
            symbol_prices = vh.data.local.get_price_history(symbol)
            symbol_prices = symbol_prices.sort_values(by='date')
            symbol_prices = symbol_prices.set_index(['date'])
            # Check dirtiness
            bad = 0
            for index, row in symbol_prices.iterrows():
                if row['open'] == row['high'] == row['low'] == row['close']:
                    bad += 1

            dirtiness = bad / symbol_prices.shape[0] if symbol_prices.shape[0] else 1.0
            if dirtiness < args.dirtlimit:
                prices_dict[symbol] = symbol_prices
            else:
                log('Price data for {0} too dirty @ {1:.2f}%.\tskipping...'.format(symbol, dirtiness * 100), force=True)

        except FileNotFoundError:
            log('FileNotFoundError @ {}\t\tskipping...'.format(symbol), force=True)

    namespace = list(prices_dict.keys())

    log('Using namespace ' + str(namespace))

    summary_report = {
        'symbol': [],
        'cash': [],
        'value': [],
        'n trades': [],
        'wl ratio': [],
        'pnl': [],
    }

    trades_report = {
        'symbol': [],
        'open@': [],
        'close@': [],
        'trade #': [],
        'pnl trade': [],
        'pnl net': [],
    }

    num_symbols = len(namespace)
    log('\nRunning Backtests...\n', force=True)

    for i, ticker in enumerate(namespace):
        print('=' * 50)
        log('Backtesting ticker @ {} - {}/{}'.format(ticker, i+1, num_symbols), force=True)

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

        # get ticker earnings
        earnings_df = vh.data.local.get_ticker_earnings(ticker, all_earnings_df)

        # init Cerebro
        cerebro = bt.Cerebro()  # create Cerebro object
        cerebro.addstrategy(strategies.MACDComposite,
                            earnings_df=earnings_df,
                            delay=args.delay,
                            verbose=args.verbose,
                            ticker=ticker,
                            sl=args.stoptrailpercent,
                            limit_percent=args.limitpercent,
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
            dataname=prices_dict[ticker],
            fromdate=from_date,
            todate=to_date,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume',
        )
        cerebro.adddata(data_feed)

        cerebro.addsizer(bt.sizers.FixedSize, stake=args.stake)  # set fixed sizer

        cerebro.broker.set_cash(args.equity)  # set initial equity
        cerebro.broker.setcommission(commission=0.001)  # set broker commission to .1%

        log('\n\tBeginning Value: {}\n\tBeginning Cash: {}'.format(cerebro.broker.getvalue(), cerebro.broker.getcash()))
        try:
            results = cerebro.run(max_cpus=4)  # loop over loaded data
        except IndexError:
            print('IndexError @ {} - continuing'.format(ticker))
            continue
        # results = cerebro.run(max_cpus=4)
        log('\n\tEnding Value: {}\n\tEnding Cash: {}'.format(cerebro.broker.getvalue(), cerebro.broker.getcash()))

        # get results
        strat = results[0]

        # populate trade history report
        pnl_net = 0.0
        for trade_i, trade in enumerate(strat.trades):
            pnl_trade = trade['pnl']
            pnl_net += pnl_trade
            trades_report['symbol'].append(ticker)
            trades_report['open@'].append(trade['open@'])
            trades_report['close@'].append(trade['close@'])
            trades_report['trade #'].append(trade_i)
            trades_report['pnl trade'].append(pnl_trade)
            trades_report['pnl net'].append(pnl_net)

        # populate summary reports
        summary_report['symbol'].append(ticker)
        summary_report['cash'].append(cerebro.broker.getcash())
        summary_report['value'].append(cerebro.broker.getvalue())
        summary_report['n trades'].append(len(strat.trades))
        summary_report['wl ratio'].append(strat.get_wl_ratio())
        summary_report['pnl'].append(pnl_net)

        if args.plot:
            log('Showing Plot for {}'.format(ticker), force=True)
            cerebro.plot()

    print('=' * 50)
    print('+' * 50)
    log('All backtesting finished.', force=True)
    if args.save:  # if saving is enabled
        from pandas import DataFrame
        args_df = DataFrame({'Name': list(vars(args).keys()), 'Value': list(vars(args).values())})
        report_summary_df = DataFrame(summary_report)
        report_trades_df = DataFrame(trades_report)
        out_path = '{}BACKTEST-{}.xlsx'.format(vh.config.SCAN_FOLDER_PATH, datetime.now().strftime('%Y-%m-%d_%H_%M'))
        vh.data.local.multi_df_to_excel(out_path, [report_summary_df, report_trades_df, args_df], ['Trade Summary',
                                                                                                   'Trade History',
                                                                                                   'Arguments'])
        log('Saved to {}'.format(out_path), force=True)

    print('+' * 50)


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

    parser.add_argument('--maxthreshpercent', '-mtp', type=float, default=0.5,
                        metavar='PERCENT',
                        help='MACD max value percent threshold (default: 0.5)')

    parser.add_argument('--triggerthreshpercent', '-ttp', type=float, default=0.8,
                        metavar='PERCENT',
                        help='MACD value percent that will trigger condition (default 0.8)')

    parser.add_argument('--stoptrailpercent', '-stp', type=float, default=0.05,
                        metavar='PERCENT',
                        help='Trailing Stop delta percent (default: 0.05)')

    parser.add_argument('--limitpercent', '-lip', type=float, default=0.03,
                        metavar='PERCENT',
                        help='Percent of price to use for Limit (default: 0.03)')

    parser.add_argument('--stake', '-st', type=int, default=10,
                        metavar='NSHARES',
                        help='Number of shares per operation (default: 10)')

    parser.add_argument('--equity', '-e', type=float, default=10000.0,
                        help='Initial equity to trade with (default: 10000.0)')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable logging small details during back-testing')

    # TODO add arg check. Plot all if no names given, plot only names given if names given
    parser.add_argument('--plot', '-p', action='store_true',
                        help='Enable plotting at the end of each ticker back-test')

    parser.add_argument('--save', '-s', action='store_true',
                        help='Save output to .xlsx file')

    parser.add_argument('--namespace', '-ns', type=str, nargs=2, default=None,
                        metavar=('TYPE', 'PATH'),
                        help='Load a namespace from a file of specified type. Types include: '
                             'tos (Think or Swim Watchlist CSV), nl (New line seperated values), all (All in dataset')

    parser.add_argument('--dirtlimit', '-dl', type=float, default=0.005,
                        metavar='LIMIT',
                        help='Set tolerable percent of dataset that can contain "dirty" values for OHLC and still'
                             'be considered clean (default: 0.005)')

    parser.add_argument('symbol', type=str, nargs='*',
                        help='Stock symbol(s) to back-test')

    # TODO add data path argument

    return parser.parse_args(pargs)


if __name__ == '__main__':
    run()

