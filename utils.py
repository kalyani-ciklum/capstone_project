"""Utility functions used throughout the Expense Tracker project."""

from datetime import datetime
from math import isfinite

CSV_HEADERS = ["ID", "Date", "Amount", "Category", "Description"]
DATE_FORMAT = "%Y-%m-%d"


def validate_date(date_text):
    """Return True if date_text is a valid date in YYYY-MM-DD format."""
    try:
        parsed_date = datetime.strptime(date_text, DATE_FORMAT)
    except ValueError:
        return False

    # The round-trip check keeps the format strict, including leading zeroes.
    return parsed_date.strftime(DATE_FORMAT) == date_text


def validate_amount(amount_text):
    """Return True if amount_text is a positive numeric value."""
    try:
        amount = float(amount_text)
    except ValueError:
        return False

    return isfinite(amount) and amount > 0


def prompt_date(prompt):
    """Keep asking the user for a date until it is valid."""
    while True:
        date_text = input(prompt).strip()

        if validate_date(date_text):
            return date_text

        print("Invalid date. Please use YYYY-MM-DD format.")


def prompt_amount(prompt):
    """Keep asking the user for an amount until it is valid."""
    while True:
        amount_text = input(prompt).strip()

        if validate_amount(amount_text):
            return float(amount_text)

        print("Invalid amount. Please enter a positive number.")


def prompt_non_empty(prompt):
    """Keep asking the user for text until it is not empty."""
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be empty.")


def get_next_id(expenses):
    """Return the next available expense ID."""
    if not expenses:
        return "1"

    highest_id = max(int(expense["ID"]) for expense in expenses)
    return str(highest_id + 1)


def display_expenses(expenses):
    """Display expenses in a simple table."""
    if not expenses:
        print("\nNo expenses found.")
        return

    print()
    print("-" * 86)
    print(
        f"{'ID':<5}"
        f"{'Date':<14}"
        f"{'Amount':<12}"
        f"{'Category':<18}"
        f"{'Description':<30}"
    )
    print("-" * 86)

    for expense in expenses:
        print(
            f"{expense['ID']:<5}"
            f"{expense['Date']:<14}"
            f"${float(expense['Amount']):<11.2f}"
            f"{expense['Category']:<18.18}"
            f"{expense['Description']:<30.30}"
        )

    print("-" * 86)


def pause():
    """Pause the program so the user can read the screen."""
    input("\nPress Enter to continue...")
