# ai_loser.py 
# The worst AI for playing Wordle because it always purposefully loses.
#
# The "strategy" of this default AI player is simply to pick the word 'LOSES'
# *every* time. Since this word is a valid choice, but does not exist in the 
# list of secret words, the AI player will always fail.
#
# This player exists primarily to test the AI capabilities of the main program,
# specifically making sure the tracked statistics can handle a 0% win rate.

import utils


def makeguess(wordlist, guesses=[], feedback=[]):
    """Guess a word from the available wordlist, (optionally) using feedback 
    from previous guesses.
    
    Parameters
    ----------
    wordlist : list of str
        A list of the valid word choices. The output must come from this list.
    guesses : list of str
        A list of the previously guessed words, in the order they were made, 
        e.g. guesses[0] = first guess, guesses[1] = second guess. The length 
        of the list equals the number of guesses made so far. An empty list 
        (default) implies no guesses have been made.
    feedback : list of lists of int
        A list comprising one list per word guess and one integer per letter 
        in that word, to indicate if the letter is correct (2), almost 
        correct (1), or incorrect (0). An empty list (default) implies no 
        guesses have been made.
    Output
    ------
    word : str
        The word chosen by the AI for the next guess.
    """

    return 'LOSES'


if __name__ == "__main__":
    wordlist = utils.readwords("allwords5.txt")
    print(f"AI: \"My next choice would be {makeguess(wordlist)}\"")
