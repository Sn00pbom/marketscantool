import argparse
from valuehunter import argschedule
import subprocess


def run(pargs=None):
    r_args = parse_args(pargs)

    asc = argschedule.ArgSchedule(r_args.schedulepath)
    for args in asc:
        command = ['python', r_args.scriptpath] + args
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

    return parser.parse_args(pargs)


if __name__ == '__main__':
    run()
