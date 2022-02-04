# utils.py
# Python library of functions related to Wordle game.
#
# Author: Matthew Eicholtz
# Inspired by: https://www.powerlanguage.co.uk/wordle/

from colorama import Fore
from datetime import datetime
import os
import pdb
from pynput import keyboard
import subprocess


def getdailysecret():
    """Find the official word of the day using an encrypted list of secret words."""
    # Read words directly from file
    f = open('dailysecret.txt', 'r')
    key = int(f.readline())  # the first line is the key to a circular Caesar cipher
    words = f.read().upper().split('\n')  # make list of encrypted words
    f.close()

    # Decrypt word for today
    jan1 = datetime.strptime('2022-01-01', '%Y-%m-%d')
    index = 196 + (datetime.today() - jan1).days  # 196 is the index of the word for January 1, 2022
    secret = ''
    for letter in words[index]:
        shift = (ord(letter) - key)
        if shift < ord('A'):
            shift += 26
        secret += chr(shift)
    
    return secret


def getfeedback(guess, secret):
    """Check whether the guess matches the secret word, providing feedback about each letter.
    
    Parameters
    ----------
    guess : str
        Word that the player guesses.
    secret : str
        Word that the player is trying to guess.

    Returns
    -------
    feedback: list
        A list of integers, one per letter in the guess, to indicate if the letter is correct (2),
        almost correct (1), or incorrect (0).
    """
    # Check for valid inputs
    if not isinstance(guess, str) or not isinstance(secret, str):
        raise TypeError("inputs must be strings")
    elif len(guess) != len(secret):
        raise ValueError("length of inputs must be equal")

    # Initialize feedback
    n = len(guess)
    feedback = [0] * n  # assume no letters match at first

    # Find correct letters
    for i in range(n):
        if guess[i] == secret[i]:
            feedback[i] = 2
    
    # Find almost correct letters (exists in the secret, but in a different position)
    letters = ''.join([letter for letter, match in zip(secret, feedback) if not match])
    for i in range(n):
        if feedback[i] != 2 and guess[i] in letters:
            feedback[i] = 1
            j = letters.index(guess[i])
            letters = letters[:j] + letters[j+1:]
    
    return feedback


def getkey(debug=False):
    """Wait for the user to press a key. Valid options include a letter, Backspace, Enter, or Escape key.
    
    Parameters
    ----------
    debug : bool, optional
        Show internal information about the key that was pressed. Default is False.

    Returns
    -------
    key: str
        A string indicating what was pressed.
    """
    with keyboard.Events() as events:
        for event in events:
            if isinstance(event, keyboard.Events.Release):
                if hasattr(event.key, 'char') and event.key.char in 'abcdefghijklmnopqrstuvwxyz':
                    return event.key.char.upper()
                elif event.key == keyboard.Key.backspace:
                    return 'backspace'
                elif event.key == keyboard.Key.enter:
                    return 'enter'
                elif event.key == keyboard.Key.esc:
                    return 'esc'
                
                if debug:
                    print(event.key)


def getversion():
    """Retrieve the current git hash to use as a 'version' number."""
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


def readwords(file, header=True, sep='\n'):
    """Return a list of uppercase words from file.
    
    Parameters
    ----------
    file : str
        The file to read from.
    header : bool, optional
        Does the file contain a single-line header? Default is True.
    sep : str, optional
        Separator between words in the file. Default is '\\n'. 

    Returns
    -------
    words: list
        A list of uppercase words.
    """
    f = open(file, 'r')
    if header:  # does the file contain a header (e.g. number of words listed)
        n = int(f.readline())
    words = f.read().upper().split(sep)  # make list of words
    f.close()

    return words


def removeletters(alphabet, guess, feedback):
    """Remove letters from the known alphabet using feedback about a guessed word.
    
    Parameters
    ----------
    alphabet : str
        String of letters that are currently valid.
    guess : str
        Word that was guessed.
    feedback: list
        A list of integers, one per letter in the guessed word, to indicate if the letter 
        is correct (2), almost correct (1), or incorrect (0).

    Returns
    -------
    leftovers: str
        String of remaining letters after discarding those guessed with feedback=0.
    """
    used = set([letter for letter, exists in zip(guess, feedback) if exists == 0])
    leftovers = "".join([letter for letter in alphabet if letter not in used])

    return leftovers
                    

def test():
    """Test utility functions for errors."""
    print('\nREADWORDS')
    print('---------')
    words = readwords('secretwords5.txt')
    print(*words, sep=' ')
    print(f'Number of words: {len(words)}')

    print('\nGETFEEDBACK')
    print('-----------')
    print(f'ABC --> XYZ = {getfeedback("ABC", "XYZ")}')
    print(f'TEST --> TEST = {getfeedback("TEST", "TEST")}')
    print(f'ADIEU --> DIALS = {getfeedback("ADIEU", "DIALS")}')
    print(f'ROBOT --> BOUND = {getfeedback("ROBOT", "BOUND")}')

    print('\nGETKEY')
    print('Press any key...')
    key = getkey()
    print(key)


def updatestats(outcome, filename="stats.txt"):
    """Update statistics file based on the outcome of a game."""
    # Force input filename to be a .txt file if extension not provided
    if '.' not in filename:
        filename = filename + '.txt'

    # Try to read data from file
    try:
        with open(filename, "r") as f:
            data = f.read().split('\n')  # make list of strings, one per stat line
    except IOError:
        print(Fore.YELLOW + f'WARNING: Unable to track stats because {filename} does not exist. Creating file now.')
        data = []

    # Load stats into dictionary
    stats = {}
    for line in data:
        if len(line) == 0:  # take care of blank lines (often happens at end of file)
            continue
        stat, value = line.split('=')
        try:
            stats[stat] = int(value)
        except:  # need something special for lists
            stats[stat] = [int(i) for i in value.split(',')]
    
    # Validate dictionary
    minstats = ['played', 'win percentage', 'current streak', 'max streak', 'guess distribution']
    if set(minstats) > set(stats.keys()):
        print(Fore.YELLOW + f'WARNING: {filename} does not contain the correct stats. Resetting file now.')
        stats = dict.fromkeys(minstats, 0)
        stats['guess distribution'] = [0] * 6
    
    # Modify stats based on outcome
    stats['played'] += 1
    if outcome != 0:
        stats['current streak'] += 1
        if stats['current streak'] > stats['max streak']:
            stats['max streak'] = stats['current streak']
        stats['guess distribution'][outcome - 1] += 1
    else:
        stats['current streak'] = 0
    stats['win percentage'] = int(sum(stats['guess distribution']) / stats['played'] * 100)

    # Write new stats to file
    with open(filename, "w") as f:
        for key, value in stats.items():
            if isinstance(value, list):
                f.write(f'{key}={",".join([str(i) for i in value])}\n')
            else:
                f.write(f'{key}={value}\n')


if __name__ == "__main__":
    test()