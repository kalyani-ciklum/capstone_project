"""Menu-driven command line interface for the Expense Tracker project."""

from expense_manager import (
    add_expense,
    delete_expense,
    get_all_expenses,
    search_expense,
)
from reports import monthly_report, total_spending
from storage import load_csv, save_csv
from utils import display_expenses, pause, prompt_non_empty

CSV_FILE = "expenses.csv"


def display_menu():
    """Print the main application menu."""
    print("\n==================================")
    print("      EXPENSE TRACKER")
    print("==================================")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Search by Category")
    print("4. Show Total Spending")
    print("5. Monthly Report")
    print("6. Delete Expense")
    print("7. Save Data")
    print("8. Exit")
    print("==================================")


def handle_search(expenses):
    """Ask for a category and show matching expenses."""
    category = prompt_non_empty("Enter category to search: ")
    matches = search_expense(expenses, category)

    if matches:
        print(f"\nExpenses found in category '{category}':")
        display_expenses(matches)
        print(f"Category total: ${total_spending(matches):.2f}")
    else:
        print(f"\nNo expenses found in category '{category}'.")


def handle_monthly_report(expenses):
    """Ask for a month and display that month's spending report."""
    while True:
        month = input("Enter month (YYYY-MM): ").strip()

        if len(month) == 7 and month[4] == "-":
            year_part, month_part = month.split("-")

            if year_part.isdigit() and month_part.isdigit():
                month_number = int(month_part)

                if 1 <= month_number <= 12:
                    break

        print("Invalid month. Please use YYYY-MM format, for example 2026-07.")

    report = monthly_report(expenses, month)

    if not report["expenses"]:
        print(f"\nNo expenses found for {month}.")
        return

    print(f"\nMonthly Report for {month}")
    display_expenses(report["expenses"])
    print(f"Monthly total: ${report['total']:.2f}")

    if report["categories"]:
        print("\nSpending by category:")
        for category, amount in report["categories"].items():
            print(f"- {category}: ${amount:.2f}")


def run_app():
    """Run the main program loop."""
    expenses = load_csv(CSV_FILE)
    print(f"Loaded {len(expenses)} expense(s) from {CSV_FILE}.")

    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            add_expense(expenses)
            pause()
        elif choice == "2":
            display_expenses(get_all_expenses(expenses))
            pause()
        elif choice == "3":
            handle_search(expenses)
            pause()
        elif choice == "4":
            print(f"\nTotal spending: ${total_spending(expenses):.2f}")
            pause()
        elif choice == "5":
            handle_monthly_report(expenses)
            pause()
        elif choice == "6":
            delete_expense(expenses)
            pause()
        elif choice == "7":
            save_csv(CSV_FILE, expenses)
            print("Data saved successfully.")
            pause()
        elif choice == "8":
            save_csv(CSV_FILE, expenses)
            print("Data saved successfully. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")
            pause()


if __name__ == "__main__":
    run_app()
