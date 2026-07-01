"""Expense management functions for adding, deleting, and searching records."""

from utils import (
    get_next_id,
    prompt_amount,
    prompt_date,
    prompt_non_empty,
)


def add_expense(expenses):
    """Add a new expense to the in-memory expense list."""
    print("\nAdd Expense")
    date = prompt_date("Enter date (YYYY-MM-DD): ")
    amount = prompt_amount("Enter amount: ")
    category = prompt_non_empty("Enter category: ")
    description = prompt_non_empty("Enter description: ")

    expense = {
        "ID": get_next_id(expenses),
        "Date": date,
        "Amount": f"{amount:.2f}",
        "Category": category,
        "Description": description,
    }

    expenses.append(expense)
    print(f"Expense added successfully with ID {expense['ID']}.")
    return expense


def delete_expense(expenses):
    """Delete an expense by ID and return True if a record was removed."""
    if not expenses:
        print("\nNo expenses available to delete.")
        return False

    print("\nDelete Expense")
    expense_id = prompt_non_empty("Enter expense ID to delete: ")

    for expense in expenses:
        if str(expense["ID"]) == expense_id:
            expenses.remove(expense)
            print(f"Expense with ID {expense_id} deleted successfully.")
            return True

    print(f"No expense found with ID {expense_id}.")
    return False


def search_expense(expenses, category):
    """Return all expenses that match the given category."""
    search_text = category.strip().lower()
    return [
        expense
        for expense in expenses
        if expense["Category"].strip().lower() == search_text
    ]


def get_all_expenses(expenses):
    """Return all expenses."""
    return expenses
