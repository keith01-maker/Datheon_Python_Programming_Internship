# Stock Portfolio Performance Tracker

A terminal-based investment portfolio tracker written in Python 3. The user enters stock ticker symbols, buy prices and share quantities. The program gets the current price of each stock (live from Yahoo Finance when possible), calculates the gain/loss per holding and for the whole portfolio, and appends the results to `portfolio_summary.csv`.

## Features

| Task requirement | Implementation |
|---|---|
| Enter ticker symbols, buy prices and share quantities | `get_ticker()`, `get_positive_number()`, `get_holding()` with input validation |
| Store portfolio positions in a dictionary | `portfolio = {symbol: {name, sector, buy_price, quantity, ...}}` built by `build_portfolio()` |
| Look up current ticker prices (live via yfinance) | `get_live_price()` uses Yahoo Finance; `get_current_price()` falls back to manual input |
| Percentage gain/loss per holding | `calculate_position()` |
| Total invested capital vs current market value | `calculate_portfolio()` |
| Log the summary to an external CSV with the `csv` module | `save_summary()` appends to `portfolio_summary.csv` using `csv.DictWriter` |

**Extras:**
- Ticker symbols are checked against the S&P 500 dataset (`constituents.csv`), and the company name and sector are shown
- Buying the same stock twice merges it, using the weighted average buy price
- Clear table output with dollar formatting and +/- signs
- Works without internet or without yfinance (prices are then typed manually)
- If `portfolio_summary.csv` is open in Excel, the user can close it and retry instead of losing the data

## Requirements

- Python 3.8 or newer (tested with Python 3.13)
- Optional: [`yfinance`](https://pypi.org/project/yfinance/) for live prices

Install the optional dependency from the repository root:

```bash
python -m pip install -r task2_portfolio/requirements.txt
```

## Files

```
task2_portfolio/
├── portfolio.py             # the program
├── constituents.csv         # S&P 500 ticker dataset (input)
├── portfolio_summary.csv    # results log (created/extended by the program)
├── requirements.txt         # optional dependency: yfinance
└── README.md
```

`constituents.csv` comes from the [datasets/s-and-p-500-companies](https://github.com/datasets/s-and-p-500-companies) repository and **must** be in the same folder as `portfolio.py`.

## How to run

From the repository root:

```bash
python task2_portfolio/portfolio.py
```

1. Enter a ticker symbol (e.g. `AAPL`), the buy price per share and the number of shares.
2. Answer `y` to add another stock, or `n` to finish.
3. The program gets the current price of each stock. If a live price is not available, it asks you to type it.
4. The results are shown as a table and appended to `portfolio_summary.csv`.

## Example output

```
Getting the current market price for each stock:
  AAPL: live price $348.22
  BRK.B: live price $546.97

--------------------------------------------------------------------------------------
Symbol   Shares        Buy    Current     Invested        Value    Gain/Loss    Gain %
--------------------------------------------------------------------------------------
AAPL         10    $150.00    $348.22    $1,500.00    $3,482.20   +$1,982.20  +132.15%
BRK.B         2    $400.00    $546.97      $800.00    $1,093.94     +$293.94   +36.74%
--------------------------------------------------------------------------------------
Total invested capital : $2,300.00
Current market value   : $4,576.14
Total gain/loss        : +$2,276.14 (+98.96%)
--------------------------------------------------------------------------------------
Summary saved to portfolio_summary.csv
```

## Calculations

| Value | Formula |
|---|---|
| Invested capital | buy price x quantity |
| Market value | current price x quantity |
| Gain/loss | market value - invested capital |
| Gain/loss % | gain/loss / invested capital x 100 |
| Weighted average buy price (same stock bought twice) | (price1 x qty1 + price2 x qty2) / (qty1 + qty2) |

The total portfolio gain/loss % is calculated from the **total** invested capital and **total** market value, not as an average of the individual percentages, so larger positions correctly have a larger effect.

## Output file: `portfolio_summary.csv`

Each run appends one row per stock plus one `TOTAL` row, all with the same timestamp. Earlier runs are kept, so the file works as a performance log.

| Column | Description |
|---|---|
| `timestamp` | Date and time of the run (`YYYY-MM-DD HH:MM:SS`) |
| `symbol` | Ticker symbol, or `TOTAL` for the portfolio total |
| `company`, `sector` | From the S&P 500 dataset |
| `quantity` | Number of shares |
| `buy_price`, `current_price` | Price per share in USD |
| `invested`, `market_value`, `gain_loss` | In USD, rounded to 2 decimals |
| `gain_loss_pct` | Gain/loss in percent, rounded to 2 decimals |

Numbers are stored without `$` signs or thousands separators so the file can be opened and calculated in Excel or other tools. The file is saved as UTF-8 with a BOM so that names such as "Estée Lauder" display correctly in Excel.

## Design decisions

- **Only S&P 500 tickers are accepted**, because the provided dataset is used to validate symbols and to show the company name and sector.
- **Ticker input is case-insensitive**: `aapl` is converted to `AAPL`, the format used in the dataset.
- **Fractional shares are allowed** (e.g. `0.5`), since many brokers support them.
- **Decimals use a dot** (`150.25`). Inputs such as `150,25`, `$150`, `0`, negative numbers and `nan` are rejected with a clear message.
- **Live price first, manual input as a fallback.** The dataset has no price column, so live prices come from Yahoo Finance through `yfinance`. If yfinance is not installed, there is no internet, or Yahoo returns no data, the program asks for the price instead of stopping.
- **Ticker symbols with a dot** (`BRK.B`, `BF.B`) are converted to Yahoo's format (`BRK-B`, `BF-B`) only when requesting the price. Everywhere else the dataset format is kept.
- **The "live" price is the latest price available from Yahoo Finance.** Outside US market hours it is the most recent closing price, and Yahoo data may be delayed.

## Error handling

| Situation | Behaviour |
|---|---|
| `constituents.csv` is missing | Clear error message and exit |
| Invalid ticker, price or quantity | Rejected, the user is asked again |
| yfinance not installed / no internet / no data | Falls back to manual price input |
| `portfolio_summary.csv` open in Excel (file locked) | The user can close the file and retry |
| `Ctrl+C` | Stops cleanly with a short message |

This project is for learning purposes and is not financial advice.
