# wordle_cli.py 
# Command-line interface version of Wordle.
#
# Author: Matthew Eicholtz
# Inspired by: https://www.powerlanguage.co.uk/wordle/

from colorama import init, Fore, Style
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
AI = False  # play with AI?


def main():
    """Play game as many times as the user wants."""
    # Setup
    init(autoreset=True)  # required for colored text
    random.seed()  # use current system time for randomness

    # Read word lists from file
    wordlist = utils.readwords(ALLWORDS)
    secretwordlist = utils.readwords(SECRETWORDS)

    # Play the game
    secret = random.choice(secretwordlist)  # random selection of the secret word
    outcome = play(secret, wordlist)
    

def printtitle():
    """Show the header for the game."""
    print()
    print('  WORDLE')
    print('=' * 10)


def printword(word='', feedback=[]):
    """Print a word, leaving blanks for missing letters.

    Parameters
    ----------
    word : str, optional
        Word to display. Default is an empty string (only display blanks).
    feedback : list, optional
        A list of integers, one per letter in the word, to indicate if the letter is correct (2),
        almost correct (1), or incorrect (0). If provided, the feedback affects the color of each
        printed letter. Default is an empty list (no feedback to show).
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
    printword()
    guesses, feedback = [''], []  # known information
    gameover = False
    while not gameover:
        if AI:
            word = makeguess()
        else:
            key = utils.getkey()
        if key in ALPHABET and len(guesses[-1]) < NUMLETTERS:  # add letter to current word
            guesses[-1] += key
            printword(guesses[-1])
        elif key == 'backspace':  # erase a letter
            guesses[-1] = guesses[-1][:-1]
            printword(guesses[-1])
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
                printword(guesses[-1], feedback[-1])

                # Check endgame conditions
                if sum(f) == NUMLETTERS * 2:
                    gameover = True
                    msg = ["Genius", "Magnificent", "Impressive", "Splendid", "Great", "Phew"]
                    print(Fore.CYAN + msg[len(guesses) - 1])
                    Style.RESET_ALL
                    return len(guesses)
                elif len(guesses) == 6:
                    gameover = True
                    print(Fore.RED + f'GAME OVER: The correct word was {secret}')
                    Style.RESET_ALL
                    return 0
                else:
                    # Start new guess
                    print()
                    guesses.append('')
                    printword(guesses[-1])

        elif key == 'esc':  # quit game
            gameover = True
            print("Thanks for playing.")
            return -1


if __name__ == "__main__":
    main()