"""
Stock Portfolio Performance Tracker.

The user enters stock ticker symbols, buy prices and share quantities.
The program gets the current price of each stock (live from Yahoo Finance
when possible, otherwise typed by the user), shows the gain/loss per holding
and for the whole portfolio, and appends the results to portfolio_summary.csv.

How to run:
    python portfolio.py
"""

import csv
import logging
import math
import sys
from datetime import datetime
from pathlib import Path

# yfinance is optional: if it is not installed, the program falls back to manual prices
try:
    import yfinance as yf
except ImportError:
    yf = None

# Hide yfinance's own error messages; this program prints its own clearer messages
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# ===== Settings =====
BASE_DIR = Path(__file__).parent
TICKER_FILE = BASE_DIR / "constituents.csv"
SUMMARY_FILE = BASE_DIR / "portfolio_summary.csv"

# Column names for portfolio_summary.csv
SUMMARY_COLUMNS = [
    "timestamp", "symbol", "company", "sector", "quantity",
    "buy_price", "current_price", "invested", "market_value",
    "gain_loss", "gain_loss_pct",
]


# ===== Functions =====
def load_tickers():
    """Read the S&P 500 CSV and return a dictionary: {symbol: {"name": ..., "sector": ...}}."""
    tickers = {}
    with open(TICKER_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            symbol = row["Symbol"].strip().upper()
            tickers[symbol] = {
                "name": row["Security"].strip(),
                "sector": row["GICS Sector"].strip(),
            }
    return tickers


def get_ticker(tickers):
    """Ask for a ticker symbol until it exists in the S&P 500 list, then return it in uppercase."""
    while True:
        symbol = input("Ticker symbol (e.g. AAPL): ").strip().upper()

        if symbol == "":
            print("  Empty input. Please type a ticker symbol.")
        elif symbol not in tickers:
            print(f"  '{symbol}' is not in the S&P 500 list. Please check the spelling.")
        else:
            return symbol


def get_positive_number(prompt):
    """Ask for a number until it is a valid number greater than 0, then return it as a float."""
    while True:
        text = input(prompt).strip()

        try:
            value = float(text)
        except ValueError:
            print("  Please enter a number, using a dot for decimals (e.g. 150.25).")
            continue

        if not math.isfinite(value):
            print("  Please enter a normal number.")
        elif value <= 0:
            print("  The number must be greater than 0.")
        else:
            return value


def get_holding(tickers):
    """Ask for one stock purchase and return it as a dictionary."""
    symbol = get_ticker(tickers)
    print(f"  -> {tickers[symbol]['name']} ({tickers[symbol]['sector']})")
    buy_price = get_positive_number("Buy price per share (USD): ")
    quantity = get_positive_number("Number of shares: ")
    return {"symbol": symbol, "buy_price": buy_price, "quantity": quantity}


def ask_yes_no(prompt):
    """Ask a yes/no question until the answer is y or n. Return True for y, False for n."""
    while True:
        answer = input(prompt).strip().lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("  Please answer 'y' (yes) or 'n' (no).")


def add_holding(portfolio, holding, tickers):
    """Add one purchase to the portfolio. If the stock is already there, merge it."""
    symbol = holding["symbol"]
    new_price = holding["buy_price"]
    new_qty = holding["quantity"]

    if symbol in portfolio:
        # Same stock bought again: combine shares and use the weighted average buy price
        old_price = portfolio[symbol]["buy_price"]
        old_qty = portfolio[symbol]["quantity"]
        total_qty = old_qty + new_qty
        average_price = (old_price * old_qty + new_price * new_qty) / total_qty

        portfolio[symbol]["quantity"] = total_qty
        portfolio[symbol]["buy_price"] = average_price
        print(f"  {symbol} was already in the portfolio. Merged: "
              f"{total_qty:g} shares at an average of ${average_price:.2f}")
    else:
        # New stock: create a new entry
        portfolio[symbol] = {
            "name": tickers[symbol]["name"],
            "sector": tickers[symbol]["sector"],
            "buy_price": new_price,
            "quantity": new_qty,
        }
        print(f"  {symbol} added to the portfolio.")


def build_portfolio(tickers):
    """Ask for stock purchases one by one until the user is done. Return the portfolio dictionary."""
    portfolio = {}

    while True:
        print()
        holding = get_holding(tickers)
        add_holding(portfolio, holding, tickers)

        if not ask_yes_no("\nAdd another stock? (y/n): "):
            break

    return portfolio


def get_live_price(symbol):
    """Try to get the latest price from Yahoo Finance. Return None if it is not possible."""
    if yf is None:
        return None

    yahoo_symbol = symbol.replace(".", "-")   # Yahoo writes BRK.B as BRK-B

    try:
        history = yf.Ticker(yahoo_symbol).history(period="5d")
        price = float(history["Close"].iloc[-1])
    except Exception:
        # No internet, Yahoo is down, unknown symbol, empty data, ... -> no live price
        return None

    if not math.isfinite(price) or price <= 0:
        return None
    return price


def get_current_price(symbol):
    """Return the current price of one stock.

    Stage 2: try a live price from Yahoo Finance first.
    If that fails, ask the user to type the price manually.
    """
    price = get_live_price(symbol)
    if price is not None:
        print(f"  {symbol}: live price ${price:,.2f}")
        return price

    print(f"  {symbol}: live price not available.")
    return get_positive_number(f"  Current price of {symbol} (USD): ")


def update_current_prices(portfolio):
    """Ask for the current price of every stock in the portfolio and store it."""
    print()
    print("Getting the current market price for each stock:")
    for symbol in portfolio:
        portfolio[symbol]["current_price"] = get_current_price(symbol)


def calculate_position(position):
    """Calculate invested capital, market value and gain/loss for one stock."""
    invested = position["buy_price"] * position["quantity"]
    market_value = position["current_price"] * position["quantity"]
    gain_loss = market_value - invested
    gain_loss_pct = gain_loss / invested * 100
    return {
        "invested": invested,
        "market_value": market_value,
        "gain_loss": gain_loss,
        "gain_loss_pct": gain_loss_pct,
    }


def calculate_portfolio(portfolio):
    """Add the results to every stock, then return the totals for the whole portfolio."""
    total_invested = 0
    total_value = 0

    for symbol in portfolio:
        results = calculate_position(portfolio[symbol])
        portfolio[symbol].update(results)      # store the results inside the position
        total_invested += results["invested"]
        total_value += results["market_value"]

    total_gain = total_value - total_invested
    total_gain_pct = total_gain / total_invested * 100   # from the totals, NOT an average of %

    return {
        "invested": total_invested,
        "market_value": total_value,
        "gain_loss": total_gain,
        "gain_loss_pct": total_gain_pct,
    }


def format_money(value, show_sign=False):
    """Format a number as US dollars, e.g. 3761 -> '$3,761.00' and -39 -> '-$39.00'."""
    if value < 0:
        sign = "-"
    elif show_sign:
        sign = "+"
    else:
        sign = ""
    return f"{sign}${abs(value):,.2f}"


# One template for every row, so the header and the data always line up
ROW_FORMAT = "{:<6} {:>8} {:>10} {:>10} {:>12} {:>12} {:>12} {:>9}"


def print_portfolio_table(portfolio, totals):
    """Print the portfolio as a table, followed by the portfolio totals."""
    header = ROW_FORMAT.format("Symbol", "Shares", "Buy", "Current",
                               "Invested", "Value", "Gain/Loss", "Gain %")
    line = "-" * len(header)

    print()
    print(line)
    print(header)
    print(line)

    for symbol, position in portfolio.items():
        print(ROW_FORMAT.format(
            symbol,
            f"{position['quantity']:g}",
            format_money(position["buy_price"]),
            format_money(position["current_price"]),
            format_money(position["invested"]),
            format_money(position["market_value"]),
            format_money(position["gain_loss"], show_sign=True),
            f"{position['gain_loss_pct']:+.2f}%",
        ))

    print(line)
    print(f"Total invested capital : {format_money(totals['invested'])}")
    print(f"Current market value   : {format_money(totals['market_value'])}")
    print(f"Total gain/loss        : {format_money(totals['gain_loss'], show_sign=True)} "
          f"({totals['gain_loss_pct']:+.2f}%)")
    print(line)


def save_summary(portfolio, totals):
    """Append this run's results to portfolio_summary.csv (one row per stock + one TOTAL row)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Write the header only when the file is new or empty
    write_header = not SUMMARY_FILE.exists() or SUMMARY_FILE.stat().st_size == 0

    with open(SUMMARY_FILE, "a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_COLUMNS)
        if write_header:
            writer.writeheader()

        for symbol, position in portfolio.items():
            writer.writerow({
                "timestamp": timestamp,
                "symbol": symbol,
                "company": position["name"],
                "sector": position["sector"],
                "quantity": position["quantity"],
                "buy_price": round(position["buy_price"], 2),
                "current_price": round(position["current_price"], 2),
                "invested": round(position["invested"], 2),
                "market_value": round(position["market_value"], 2),
                "gain_loss": round(position["gain_loss"], 2),
                "gain_loss_pct": round(position["gain_loss_pct"], 2),
            })

        # One extra row with the totals for the whole portfolio
        writer.writerow({
            "timestamp": timestamp,
            "symbol": "TOTAL",
            "invested": round(totals["invested"], 2),
            "market_value": round(totals["market_value"], 2),
            "gain_loss": round(totals["gain_loss"], 2),
            "gain_loss_pct": round(totals["gain_loss_pct"], 2),
        })

    print(f"Summary saved to {SUMMARY_FILE.name}")


def save_summary_with_retry(portfolio, totals):
    """Save the summary. If the file is locked (e.g. open in Excel), let the user retry."""
    while True:
        try:
            save_summary(portfolio, totals)
            return
        except PermissionError:
            print(f"Could not write {SUMMARY_FILE.name}. It may be open in another program (e.g. Excel).")
            if not ask_yes_no("Close the file, then try again? (y/n): "):
                print("The summary was NOT saved.")
                return


def main():
    """Main program: collect the portfolio, get prices, show the results and save them."""
    print("=" * 40)
    print("   STOCK PORTFOLIO PERFORMANCE TRACKER")
    print("=" * 40)

    # --- Load the ticker list, with error handling ---
    try:
        tickers = load_tickers()
    except FileNotFoundError:
        print(f"Error: ticker file not found at:\n  {TICKER_FILE}")
        print("Make sure constituents.csv is in the same folder as portfolio.py.")
        sys.exit(1)

    if not tickers:
        print("Error: the ticker file is empty.")
        sys.exit(1)

    if yf is None:
        print("Note: yfinance is not installed, so prices must be entered manually.")
        print("      Install it with: python -m pip install yfinance")

    portfolio = build_portfolio(tickers)
    update_current_prices(portfolio)
    totals = calculate_portfolio(portfolio)
    print_portfolio_table(portfolio, totals)
    save_summary_with_retry(portfolio, totals)


# ===== Program entry point =====
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C, or input closed (Ctrl+Z on Windows / Ctrl+D on Linux & macOS)
        print("\n\nProgram stopped. Nothing was saved in this run.")