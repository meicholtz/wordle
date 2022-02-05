# WORDLE

Play the addictive daily word game as much as you want in this Python variant with optional integration of artificial intelligence (AI). Inspired by the [original web-based version](https://www.powerlanguage.co.uk/wordle/) developed by Josh Wardle.

***NOTE: This repository was created for learning purposes in CSC 3510 (Introduction to Artificial Intelligence) at Florida Southern College.***

## Requirements

The code provided here was developed in Python 3.9.5 on Windows 10 using VS Code and a Git Bash terminal. Setup and usage may vary slightly for other operating systems or software tools. At a minimum, you will need the following Python libraries installed:

- colorama
- pynput
- six
- tqdm

In addition, the instructions that follow assume you have properly installed git on your machine. Click [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) if you need help doing that.

## Setup

1. The best way to use this code is to [clone the repository](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) to your local machine. To do so in VS Code, open a terminal and navigate to the parent directory of your choice using the `cd` command, e.g.:

        $ cd ~/Documents/csc3510

    Then, use `git clone` to create a new subdirectory called wordle with the code from this repository:

        $ git clone https://github.com/meicholtz/wordle

    Go into the directory and make sure the appropriate files are there by using the `ls` command:

        $ cd wordle
        $ ls

2. Before running the code, you need to make sure the required libraries are installed. The recommended way to do this is to [create a virtual environment](https://docs.python.org/3/library/venv.html) so that you can have separate environments for different projects. To create a virtual environment, use the `venv` command:

        $ python -m venv /path/to/new/virtual/environment

    If you do not have a preferred location for your environments, try putting them in a hidden folder in your home directory, such as:

        $ python -m venv ~/.venv/wordle

    Next, you need to activate the virtual environment using the `source` command:

        $ source ~/.venv/wordle/Scripts/activate

    You will know that you have done it correctly if you see the environment name in parentheses in your terminal, e.g. (wordle). After you are in your virtual environment, use `pip install` to install the libraries you need. It is easiest to do this with the requirements.txt file provided in the repository.

        $ pip install -r requirements.txt
        $ pip list

    Note that the second command above will list all installed libraries, which is useful for verification purposes.

## Usage

Use the following commands to play the game:

- To play Wordle as a human player,

        $ python wordle.py

- To play Wordle using an AI player,

        $ python wordle.py -ai ai_player

    where ai_player is the name of any file that contains the function `makeguess(wordlist, guesses, feedback)`. As an example, the most basic AI player (i.e. random guessing) is provided in the file ai_dummy.py. To use that AI player,

        $ python wordle.py -ai ai_dummy

There are several additional optional parameters that can be passed to wordle.py.

- If you want to speed up gameplay when using an AI player, use

        $ python wordle.py -ai ai_player --fast

- If you do ***not*** want to track statistics when playing the game (see stats.txt), use

        $ python wordle.py --practice

    or

        $ python wordle.py -ai ai_player --practice
