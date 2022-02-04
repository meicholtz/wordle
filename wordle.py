# wordle.py 
# Command-line interface version of Wordle powered by Python.
#
# Author: Matthew Eicholtz
# Inspired by: https://www.powerlanguage.co.uk/wordle/

import argparse
import check_stats
from colorama import init, Fore, Style
import importlib
import os
import pdb
import random
import time
from tqdm import tqdm
import utils

ROOT = os.path.dirname(os.path.realpath(__file__))
SECRETWORDS = os.path.join(ROOT, "secretwords5.txt")
ALLWORDS = os.path.join(ROOT, "allwords5.txt")
MAXATTEMPTS = 6  # how many total guesses are allowed?
NUMLETTERS = 5  # how many letters in the word?
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # valid letters to guess

parser = argparse.ArgumentParser(description="Play Wordle in Python!")
parser.add_argument('-ai', metavar='filename', type=str, help='name of AI file containing makeguess function')
parser.add_argument('-n', metavar='numgames', type=int, help='number of games to play', default=1)
parser.add_argument('--seed', metavar='s', type=int, help='seed for random number generation, defaults to system time')
parser.add_argument('--stats', '-s', metavar='filename', type=str, help='name of stats file, defaults to stats.txt', default='stats.txt')
parser.add_argument('--fast', action='store_true', help='flag to speed up the game (AI only)')
parser.add_argument('--superfast', action='store_true', help='flag to eliminate any printed display during the game (AI only)')
parser.add_argument('--playall', action='store_true', help="flag to play all possible secret words")
parser.add_argument('--practice', action='store_true', help='flag to not track stats for this game')
parser.add_argument('--daily', action='store_true', help="flag to play today's Wordle")
parser.add_argument('--showfails', action='store_true', help='flag to display the secret words that were missed after all games are complete')
parser.add_argument('--version', action='version', version=utils.getversion())


def main(args):
    # Setup
    init(autoreset=True)  # required for colored text

    if args.seed is None:
        random.seed()  # use current system time for randomness
    else:
        random.seed(args.seed)  # use seed provided by user
    
    if args.fast:
        delay = 0
    else:
        delay = 1

    if args.playall and (args.daily or args.n > 1):
        print(Fore.RED + f'ERROR: Invalid set of input arguments. Cannot set -n or --daily if using --playall.')
        return 0
    
    # Load AI player (if provided)
    ai = args.ai
    if ai is not None:
        print("Loading AI player...", end="")
        try:
            ai = importlib.import_module(ai.split('.')[0])  # split removes extension if provided
        except ImportError:
            print(Fore.RED + f"\n\tERROR: Cannot import AI player from file ({ai})")
            return 0

        if not hasattr(ai, 'makeguess'):
            print(Fore.RED + f"\n\tERROR: This AI player does not have a 'makeguess' function")
            return 0
        print("done")
        print("Playing games...")

    # Read word lists from file
    wordlist = utils.readwords(ALLWORDS)
    secretwordlist = utils.readwords(SECRETWORDS)

    # Play the game
    failures = []  # keep track of which secret words were missed
    if args.playall:
        args.n = len(secretwordlist)
    for i in tqdm(range(args.n)) if args.superfast else range(args.n):
        # Set the secret word
        if args.daily:  # use the official word of the day
            secret = utils.getdailysecret()
        elif args.playall:  # iterate through the entire secret word list
            secret = secretwordlist[i]
        else:  # pick randomly
            secret = random.choice(secretwordlist)
        
        # Who is playing?
        if ai is None:  # human player
            outcome = play(secret, wordlist)
        else:  # AI player
            outcome = watch(secret, wordlist, ai, delay, verbose=not args.superfast)
        
        # Was the word missed?
        if outcome <= 0:
            failures.append(secret)

        # Update statistics file
        if outcome != -1 and not args.practice:  # only update if user didn't quit
            utils.updatestats(outcome, filename=args.stats)

    # Show updated stats if not practicing
    if not args.practice:
        check_stats.main(args.stats)

    # Show failed words, if requested
    if args.showfails and len(failures) > 0:
        print("\nFAILED WORDS")
        print("=" * 12)
        failures.sort()
        print(*failures, sep='\n')
        print()


def printtitle():
    """Show the header for the game."""
    print()
    print('  WORDLE')
    print('=' * 10, end=" ")
    print("Remaining Letters...")


def printword(word='', feedback=[], remaining=''):
    """Print a word, leaving blanks for missing letters.

    Parameters
    ----------
    word : str, optional
        Word to display. Default is an empty string (only display blanks).
    feedback : list, optional
        A list of integers, one per letter in the word, to indicate if the letter is correct (2),
        almost correct (1), or incorrect (0). If provided, the feedback affects the color of each
        printed letter. Default is an empty list (no feedback to show).
    remaining : str, optional
        String containing the remaining letters that could be in the word.
        By default, this argument is empty.
    """
    print('\r', end='')  # move the cursor to the left of the line
    if len(feedback) == 0:  # show the word as the user is typing it
        print(*word.upper(), sep=' ', end=' ' if len(word) > 0 else '')
        print('_ ' * (NUMLETTERS - len(word)), end='')  # add blanks for missing letters
    else:  # show the word with colored feedback after the user submitted it
        for i in range(NUMLETTERS):
            if feedback[i] == 2:  # correct
                print(Fore.GREEN + word[i] + ' ', end='')
            elif feedback[i] == 1:  # almost correct
                print(Fore.YELLOW + word[i] + ' ', end='')
            elif feedback[i] == 0:  # incorrect
                print(Fore.WHITE + word[i] + ' ', end='')
        Style.RESET_ALL
    print(' ' + remaining, end=' ')


def play(secret, wordlist):
    """Play Wordle using a secret word and a list of acceptable guesses.

    Parameters
    ----------
    secret : str
        Word that the player is attempting to guess.
    wordlist : list of str
        List of strings comprising valid guesses during the game.
    """
    printtitle()
    printword(remaining=ALPHABET)

    guesses, feedback = [''], []  # known information
    leftovers = ALPHABET  # remaining letters
    gameover = False
    while not gameover:
        key = utils.getkey()
        if key in ALPHABET and len(guesses[-1]) < NUMLETTERS:  # add letter to current word
            guesses[-1] += key
            printword(guesses[-1], remaining=leftovers)
        elif key == 'backspace':  # erase a letter
            guesses[-1] = guesses[-1][:-1]
            printword(guesses[-1], remaining=leftovers)
        elif key == 'enter':  # submit word if finished
            if len(guesses[-1]) < NUMLETTERS:
                msg = "Not enough letters"
                print(Fore.RED + msg, end='')
                Style.RESET_ALL
                time.sleep(1)
                print('\b' * len(msg) + " " * len(msg) + '\b' * len(msg), end='')
            elif guesses[-1] not in wordlist:
                msg = "Not in word list"
                print(Fore.RED + msg, end='')
                Style.RESET_ALL
                time.sleep(1)
                print('\b' * len(msg) + " " * len(msg) + '\b' * len(msg), end='')
            else:
                # Check guess
                f = utils.getfeedback(guesses[-1], secret)
                feedback.append(f)

                # Show feedback as colored text
                printword(guesses[-1], feedback[-1], leftovers)

                # Check endgame conditions
                if sum(f) == NUMLETTERS * 2:
                    gameover = True
                    msg = ["Genius", "Magnificent", "Impressive", "Splendid", "Great", "Phew"]
                    print(Fore.CYAN + '\n' + msg[len(guesses) - 1])
                    Style.RESET_ALL
                    return len(guesses)
                elif len(guesses) == 6:
                    gameover = True
                    print(Fore.RED + f'\nGAME OVER: The correct word was {secret}')
                    Style.RESET_ALL
                    return 0
                else:
                    # Start new guess
                    print()
                    leftovers = utils.removeletters(leftovers, guesses[-1], feedback[-1])
                    guesses.append('')
                    printword(guesses[-1], remaining=leftovers)

        elif key == 'esc':  # quit game
            gameover = True
            print("\nThanks for playing.")
            return -1


def watch(secret, wordlist, ai, delay=1, verbose=True):
    """Play Wordle using a secret word, a list of acceptable guesses, and an AI player.

    Parameters
    ----------
    secret : str
        Word that the player is attempting to guess.
    wordlist : list of str
        List of strings comprising valid guesses during the game.
    ai : module
        AI player module that must include a function called makeguess.
    delay : float, optional
        Number of seconds to wait between guesses. Default is 1.
    """
    if verbose:
        printtitle()
        printword(remaining=ALPHABET)

    guesses, feedback = [], []  # known information
    leftovers = ALPHABET  # remaining letters
    gameover = False
    while not gameover:
        # Ask AI player for next guess
        guess = ai.makeguess(wordlist, guesses, feedback)
        guesses.append(guess)
        
        if verbose:
            printword(guesses[-1], remaining=leftovers)
            time.sleep(delay)

        if guesses[-1] not in wordlist:
            if verbose:
                print(Fore.RED + "Not in word list", end='')
                print('\nThanks for playing')
            return -1
        else:
            # Check guess
            f = utils.getfeedback(guesses[-1], secret)
            feedback.append(f)

            # Show feedback as colored text
            if verbose:
                printword(guesses[-1], feedback[-1], leftovers)

            # Check endgame conditions
            if sum(f) == NUMLETTERS * 2:
                gameover = True
                if verbose:
                    msg = ["Genius", "Magnificent", "Impressive", "Splendid", "Great", "Phew"]
                    print(Fore.CYAN + '\n' + msg[len(guesses) - 1])
                    Style.RESET_ALL
                return len(guesses)
            elif len(guesses) == 6:
                gameover = True
                if verbose:
                    print(Fore.RED + f'\nGAME OVER: The correct word was {secret}')
                    Style.RESET_ALL
                return 0
            else:
                # Start new guess
                if verbose:
                    print()
                leftovers = utils.removeletters(leftovers, guesses[-1], feedback[-1])


if __name__ == "__main__":
    main(parser.parse_args())
