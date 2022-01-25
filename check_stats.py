# check_stats.py
# Simple script to read and display stats from file.

from colorama import init, Fore
import pdb


def main():
    init(autoreset=True)  # required for colored text

    # Read data from stats file
    try:
        with open("stats.txt", "r") as f:
            data = f.read().split('\n')  # make list of strings, one per stat line
    except IOError:
        print(Fore.RED + 'ERROR: stats.txt does not exist. Check files in directory.')
        return 0

    # Display stats
    print("\nSTATISTICS")
    print("=" * 10)
    for line in data:
        stat, value = line.split('=')  # expected format is "stat=value"
        print(f'{stat.title()}: {value}')
    print()
    # pdb.set_trace()


if __name__ == "__main__":
    main()