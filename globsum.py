import pandas as pd
from pandas import DataFrame
from os import listdir, mkdir
from os.path import isfile, join
import argparse
import datetime as dt
import importlib.util
import valuehunter as vh


def build(scheme, paths) -> DataFrame:
    rows = []
    for path in paths:
        row = [str(path)]
        try:
            d = {name: pd.read_excel(path, index_col=None, sheet_name=name, engine='openpyxl')
                 for name in ['Trade Summary', 'Trade History', 'Arguments']}
            arg_df = d['Arguments']
            for v in arg_df['Value']:
                row.append(v)

            for k, f in scheme.items():
                row.append(f(d))

        except KeyError:
            print(path, 'incompatible. Skipping...')
            continue

        rows.append(row)

    columns = ['path', 'simweights', 'delay', 'macd', 'anychain',
               'chainlenlookback', 'triggerchainlen', 'maxthreshpercent',
               'triggerthreshpercent', 'stoptrailpercent', 'limitpercent',
               'stake', 'equity', 'verbose', 'plot', 'save', 'namespace',
               'dirtlimit', 'symbol']
    columns += [k for k in scheme.keys()]
    df = DataFrame(rows, columns=columns)
    return df


def run(pargs=None):
    args = parse_args(pargs)

    # import scheme from args
    spec = importlib.util.spec_from_file_location('module.name', args.schemepath)
    scheme_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scheme_module)

    # get .xlsx files in source folder
    folder_path = args.sourcefolder
    paths = [join(folder_path, f) for f in listdir(folder_path) if isfile(join(folder_path, f)) and f.endswith('.xlsx')]

    # build (and save) DataFrame
    print('Working...')
    df = build(scheme_module.SCHEME, paths)
    vh.data.local.multi_df_to_excel(args.output, [df], ['Global Summary'])
    print('Saved global summary to', args.output)


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Build global summary Excel file from backtesting results folder.'
    )

    parser.add_argument('schemepath',
                        metavar='SCHEMEPATH',
                        help='Path to a scheme.py containing dict named SCHEME s.t. columnname: lambda')

    parser.add_argument('sourcefolder', nargs='?', default='./',
                        metavar='SOURCEFOLDERPATH',
                        help='Path to folder containing backtest output .xlsx files (default: ./)')

    parser.add_argument('--output', '-o', default='./GLOBSUM{}.xlsx'.format(dt.datetime.now().date()),
                        metavar='OUTPATH',
                        help='Path to output global summary .xlsx file to. Set to NONE to disable saving '
                             '(default "./GLOBSUMYYYY-MM-DD.xlsx")')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    run()

