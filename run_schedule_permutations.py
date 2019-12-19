import argparse
import subprocess

from valuehunter import argschedule


def run(pargs=None):
    r_args = parse_args(pargs)

    asc = argschedule.ArgSchedule(r_args.schedulepath)
    for args in asc:
        command = [r_args.pyname, r_args.scriptpath] + args
        print('Running command:', command)
        subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print('Finished')


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(description='Run a python script over every argument permutation in a schedule')

    parser.add_argument('scriptpath',
                        metavar='SCRIPTPATH',
                        help='Path to python script to run argument permutations on')

    parser.add_argument('schedulepath',
                        metavar='SCHEDULEPATH',
                        help='Path to a schedule.json with schedule formatting')

    parser.add_argument('--pyname', '-pn', default='python',
                        metavar='PYTHONNAME',
                        help='Name of python executable or path (default: python)')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    run()
