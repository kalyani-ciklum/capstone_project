"""Reporting functions for expense totals and monthly summaries."""


def total_spending(expenses):
    """Return the total amount spent across all expenses."""
    return sum(float(expense["Amount"]) for expense in expenses)


def spending_by_category(expenses):
    """Return spending totals grouped by category."""
    categories = {}

    for expense in expenses:
        category = expense["Category"]
        categories[category] = categories.get(category, 0) + float(
            expense["Amount"]
        )

    return categories


def monthly_report(expenses, month):
    """Return all expenses and totals for a month in YYYY-MM format."""
    monthly_expenses = [
        expense for expense in expenses if expense["Date"].startswith(month)
    ]

    return {
        "expenses": monthly_expenses,
        "total": total_spending(monthly_expenses),
        "categories": spending_by_category(monthly_expenses),
    }
