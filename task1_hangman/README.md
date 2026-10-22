# Hangman (Terminal Game)

A terminal-based Hangman game written in Python 3. The player guesses a hidden word letter by letter, with a limit of **6 mistakes**. Each wrong guess adds one part to an ASCII gallows drawing.

## Features

| Task requirement | Implementation |
|---|---|
| Guess the word letter by letter within 6 attempts | `play_game()` with `MAX_MISTAKES = 6` |
| ASCII gallows art that updates with each wrong guess | `HANGMAN_STAGES` (7 stages, index = number of mistakes) |
| Track previously guessed letters | `guessed` is a `set`, shown every turn |
| Duplicate guesses do not cost a life | Checked **before** the guess is recorded, then `continue` with no penalty |
| Select a word with `random.choice()` | From `google-10000-english-no-swears.txt` |
| Masked word display (e.g. `_ A _ H E O N`) | `get_masked_word()` |

**Extras:**
- Input validation: empty input, more than one letter, and characters outside a-z are rejected with no penalty
- Play-again option with a win/loss score
- Clear error message if the word file is missing
- Clean exit when the player presses `Ctrl+C`

## Requirements

- Python 3.8 or newer (tested with Python 3.13)
- Standard library only (`random`, `string`, `sys`, `pathlib`), nothing to install

## Folder structure

```
task1_hangman/
├── hangman.py
├── google-10000-english-no-swears.txt
└── README.md
```

The word list file **must** be in the same folder as `hangman.py`.

## How to run

```bash
python hangman.py
```

## How to play

1. The program picks a random secret word.
2. Type one letter and press Enter.
3. A correct letter is revealed in the word. A wrong letter adds one part to the drawing.
4. You **win** when every letter is revealed, and **lose** after 6 mistakes.
5. When the round ends, type `y` to play again or `n` to quit.

## Example output

```
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
Word      : _ A _ _ E _
Mistakes  : 3/6
Guessed   : A, D, E, F, Y
Guess a letter: t
  Correct! 'T' is in the word.
```

## Design decisions

- **Guesses are case-insensitive.** The task does not specify this, so the game follows the usual Hangman rule: `A` is the same as `a`. Both the player's input and the word list are converted to lowercase before comparing, while the display uses uppercase to match the example in the task (`_ A _ H E O N`).
- **Word length is limited to 5-10 letters.** The word list has 9,894 words, including 1-2 letter words (such as `a` and `pm`) that end a round almost instantly, as well as very long words. After filtering, 6,976 words remain. The limits can be changed with `MIN_LEN` and `MAX_LEN`.
- **Repeated guesses are never counted as mistakes**, whether the letter is right or wrong, as required by the task.
