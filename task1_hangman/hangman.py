"""
Hangman - a terminal-based word guessing game.

The player guesses a hidden word letter by letter, with a limit of 6 mistakes.
Each wrong guess adds one part to the ASCII gallows drawing.
Letters that were already guessed are not counted as a mistake again.

How to run:
    python hangman.py
"""

import random
import string
import sys
from pathlib import Path

# ===== Settings =====
BASE_DIR = Path(__file__).parent
WORD_FILE = BASE_DIR / "google-10000-english-no-swears.txt"
MIN_LEN = 5        # minimum word length
MAX_LEN = 10       # maximum word length
MAX_MISTAKES = 6   # maximum number of wrong guesses

# ===== Gallows ASCII art =====
# List index = number of mistakes (0 to 6)
HANGMAN_STAGES = [
    r"""
  +---+
  |   |
      |
      |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========""",
]

# Safety check: number of stages must be MAX_MISTAKES + 1
assert len(HANGMAN_STAGES) == MAX_MISTAKES + 1, "Number of stages does not match MAX_MISTAKES"


# ===== Functions =====
def get_masked_word(secret_word, guessed):
    """Turn the secret word into a masked display, e.g. 'D _ A _ _ _ D'."""
    return " ".join(letter.upper() if letter in guessed else "_" for letter in secret_word)


def get_guess():
    """Ask the player for one letter until the input is valid, then return it in lowercase."""
    while True:
        guess = input("Guess a letter: ").strip().lower()   # normalize INPUT to lowercase

        if len(guess) == 0:
            print("  Empty input. Please type one letter.")
        elif len(guess) > 1:
            print("  Please type only ONE letter.")
        elif guess not in string.ascii_lowercase:
            print("  That is not a letter from a to z.")
        else:
            return guess


def play_game(secret_word):
    """Play one round of Hangman. Return True if the player wins, False if they lose."""
    guessed = set()    # every letter guessed so far (right or wrong)
    mistakes = 0       # number of wrong guesses

    while mistakes < MAX_MISTAKES:
        # --- 1. Show the current state ---
        print(HANGMAN_STAGES[mistakes])                      # drawing for the current mistake count
        print("Word      :", get_masked_word(secret_word, guessed))
        print(f"Mistakes  : {mistakes}/{MAX_MISTAKES}")
        print("Guessed   :", ", ".join(sorted(guessed)).upper() or "-")

        # --- 2. Ask for a guess ---
        guess = get_guess()

        # --- 3. Duplicate rule: check BEFORE recording the guess ---
        if guess in guessed:
            print(f"  You already guessed '{guess.upper()}'. No penalty.")
            continue

        # --- 4. Record the guess ---
        guessed.add(guess)

        # --- 5. Right or wrong? ---
        if guess in secret_word:
            print(f"  Correct! '{guess.upper()}' is in the word.")
            if set(secret_word) <= guessed:      # letters(word) ⊆ guessed → win
                print()
                print("Word      :", get_masked_word(secret_word, guessed))
                print("Congratulations, you WIN!")
                return True
        else:
            mistakes += 1
            print(f"  Wrong! '{guess.upper()}' is not in the word.")

    # The loop ended because mistakes reached MAX_MISTAKES → the player loses
    print(HANGMAN_STAGES[mistakes])                          # full drawing
    print(f"Out of attempts. You LOSE. The word was: {secret_word.upper()}")
    return False


def load_words():
    """Read the word file, normalize it to lowercase, then filter by length."""
    with open(WORD_FILE, "r", encoding="utf-8") as file:
        words = file.read().lower().split()   # normalize DATA to lowercase
    return [word for word in words if MIN_LEN <= len(word) <= MAX_LEN]


def ask_play_again():
    """Ask whether the player wants another round. Repeat until the answer is y or n."""
    while True:
        answer = input("\nPlay again? (y/n): ").strip().lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("  Please answer 'y' (yes) or 'n' (no).")


def main():
    """Main program: load the words once, then repeat rounds while the player wants to."""
    # --- Load the words, with error handling ---
    try:
        valid_words = load_words()     # the file is read only ONCE
    except FileNotFoundError:
        print(f"Error: word file not found at:\n  {WORD_FILE}")
        print("Make sure the file is in the same folder as hangman.py.")
        sys.exit(1)

    if not valid_words:
        print(f"Error: no words of length {MIN_LEN}-{MAX_LEN} found in the word file.")
        sys.exit(1)

    wins = 0
    losses = 0

    print("=" * 35)
    print("        WELCOME TO HANGMAN")
    print(f"  Guess the word, max {MAX_MISTAKES} mistakes!")
    print("=" * 35)

    while True:
        secret_word = random.choice(valid_words)   # new word every round

        if play_game(secret_word):                 # True = win, False = lose
            wins += 1
        else:
            losses += 1

        print(f"Current score -> Wins: {wins} | Losses: {losses}")

        if not ask_play_again():                   # answer 'n' → leave the loop
            break

    print()
    print("=" * 35)
    print(f"  Game over. Wins: {wins} | Losses: {losses}")
    print("  Thanks for playing!")
    print("=" * 35)


# ===== Program entry point =====
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C, or input closed (Ctrl+Z on Windows / Ctrl+D on Linux & macOS)
        print("\n\nGame stopped. Goodbye!")