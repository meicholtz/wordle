# check_stats.py
# Simple script to read and display stats from file.

import argparse
from colorama import init, Fore
import pdb

parser = argparse.ArgumentParser(description="Check your Wordle stats")
parser.add_argument('--filename', '-f', metavar='f', type=str, help='name of stats file to load, defaults to stats.txt', default='stats.txt')


def main(filename):
    init(autoreset=True)  # required for colored text

    # Read data from stats file
    try:
        with open(filename, "r") as f:
            data = f.read().split('\n')  # make list of strings, one per stat line
    except IOError:
        print(Fore.RED + 'ERROR: {filename} does not exist. Check files in directory.')
        return 0

    # Display stats
    print("\nSTATISTICS")
    print("=" * 10)
    for line in data:
        if len(line) == 0:  # take care of blank lines (often happens at end of file)
            continue
        stat, value = line.split('=')  # expected format is "stat=value"
        print(f'{stat.title()}: {value}')
    guesses = [int(i) for i in value.split(',')]
    mean_guess = sum([(i + 1) * x for i, x in enumerate(guesses)]) / sum(guesses)
    print(f"Average Number of Guesses to Solve: {mean_guess:0.2f}")
    # pdb.set_trace()


if __name__ == "__main__":
    args = parser.parse_args()
    main(filename=args.filename)