# wordle.py 
# Command-line interface version of Wordle powered by Python.
#
# Author: Matthew Eicholtz
# Inspired by: https://www.powerlanguage.co.uk/wordle/

import argparse
from colorama import init, Fore, Style
import importlib
import os
import pdb
import random
import time
import utils

ROOT = os.path.dirname(os.path.realpath(__file__))
SECRETWORDS = os.path.join(ROOT, "secretwords5.txt")
ALLWORDS = os.path.join(ROOT, "allwords5.txt")
MAXATTEMPTS = 6  # how many total guesses are allowed?
NUMLETTERS = 5  # how many letters in the word?
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # valid letters to guess

parser = argparse.ArgumentParser(description="Play Wordle in Python!")
parser.add_argument('-ai', metavar='filename', type=str, help='name of AI file containing makeguess function')
parser.add_argument('-n', metavar='numgames', type=int, help='number of games (AI only)', default=1)
parser.add_argument('--fast', action='store_true', help='speed up the game (AI only)')
parser.add_argument('--practice', action='store_false', help='do not track stats for this game')
parser.add_argument('--version', action='version', version=utils.getversion())


def main(args):
    # Setup
    init(autoreset=True)  # required for colored text
    random.seed()  # use current system time for randomness
    if args.fast:
        delay = 0
    else:
        delay = 1

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

    # Read word lists from file
    wordlist = utils.readwords(ALLWORDS)
    secretwordlist = utils.readwords(SECRETWORDS)

    # Play the game
    if ai is None:  # human player
        secret = random.choice(secretwordlist)  # random selection of the secret word
        outcome = play(secret, wordlist)
            
        # Update statistics file
        if outcome != -1 and args.practice:  # only update if user didn't quit
            utils.updatestats(outcome)
    else:  # ai player
        for i in range(args.n):
            secret = random.choice(secretwordlist)  # random selection of the secret word
            outcome = watch(secret, wordlist, ai, delay)

            # Update statistics file
            if outcome != -1 and args.practice:  # only update if user didn't quit
                utils.updatestats(outcome)


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


def watch(secret, wordlist, ai, delay=1):
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
    printtitle()
    printword(remaining=ALPHABET)

    guesses, feedback = [], []  # known information
    leftovers = ALPHABET  # remaining letters
    gameover = False
    while not gameover:
        # Ask AI player for next guess
        guess = ai.makeguess(wordlist, guesses, feedback)
        guesses.append(guess)
        
        printword(guesses[-1], remaining=leftovers)
        time.sleep(delay)

        if guesses[-1] not in wordlist:
            print(Fore.RED + "Not in word list", end='')
            print('\nThanks for playing')
            return -1
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


if __name__ == "__main__":
    main(parser.parse_args())
