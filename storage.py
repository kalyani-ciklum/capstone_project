"""CSV loading and saving functions for the Expense Tracker project."""

import csv
import os

from utils import CSV_HEADERS, validate_amount, validate_date


def load_csv(filename):
    """Load expenses from a CSV file and return them as a list of dictionaries."""
    expenses = []

    if not os.path.exists(filename):
        save_csv(filename, expenses)
        return expenses

    with open(filename, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames != CSV_HEADERS:
            return expenses

        for row in reader:
            # Skip invalid rows instead of crashing the application on startup.
            if not _is_valid_row(row):
                continue

            expenses.append(
                {
                    "ID": row["ID"],
                    "Date": row["Date"],
                    "Amount": f"{float(row['Amount']):.2f}",
                    "Category": row["Category"].strip(),
                    "Description": row["Description"].strip(),
                }
            )

    return expenses


def save_csv(filename, expenses):
    """Save the expense list to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(expenses)


def _is_valid_row(row):
    """Return True when a CSV row has all required valid fields."""
    required_fields = ["ID", "Date", "Amount", "Category", "Description"]

    for field in required_fields:
        if field not in row or row[field] is None:
            return False

    return (
        row["ID"].strip().isdigit()
        and validate_date(row["Date"])
        and validate_amount(row["Amount"])
        and bool(row["Category"].strip())
        and bool(row["Description"].strip())
    )
