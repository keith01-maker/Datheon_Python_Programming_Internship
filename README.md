# Datheon Python Programming Internship

A collection of Python projects built during the Datheon Python Programming Internship. Each project lives in its own folder with its own README that explains how it works and how to run it.

## Projects

| No | Project | Description | Status |
|---|---|---|---|
| 1 | [Hangman Game](task1_hangman/) | Terminal word-guessing game with ASCII gallows art, guessed-letter tracking and no penalty for repeated guesses | Done |
| 2 | [Stock Portfolio Tracker](task2_portfolio/) | Portfolio tracker with live prices (yfinance, with manual fallback), gain/loss per holding and a CSV performance log | Done |
| 3 | File Organizer | Automation script that sorts files into category folders by extension, handling naming collisions and permission errors | In progress |
| 4 | Support Chatbot | Rule-based customer support chatbot using keywords, regular expressions and a JSON FAQ dataset | In progress |

## Requirements

- Python 3.8 or newer (developed and tested with Python 3.13)
- Task 2 optionally uses `yfinance` for live prices:

```bash
python -m pip install -r task2_portfolio/requirements.txt
```

Each project lists its requirements in its own README.

## How to run a project

From the root of this repository:

```bash
python task1_hangman/hangman.py
python task2_portfolio/portfolio.py
```

See each project's README for details.

## Repository structure

```
Datheon_Python_Programming_Internship/
├── README.md
├── .gitignore
├── task1_hangman/
│   ├── hangman.py
│   ├── google-10000-english-no-swears.txt
│   └── README.md
└── task2_portfolio/
    ├── portfolio.py
    ├── constituents.csv
    ├── portfolio_summary.csv
    ├── requirements.txt
    └── README.md
```

## Author

Kurniawan Sandi ([@keith01-maker](https://github.com/keith01-maker))
