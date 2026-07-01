# Expense Tracker CLI

A beginner-friendly Python command line application for recording and reviewing
personal expenses. The project uses only Python standard libraries and stores
all expense data in a CSV file.

## Features

- Add expenses with ID, date, amount, category, and description
- View all saved expenses
- Search expenses by category
- Show total spending
- Generate a monthly spending report
- Delete an expense by ID
- Save data manually
- Automatically load data on startup
- Automatically save data when exiting
- Validate user input for dates, amounts, and required text fields

## Folder Structure

```text
Expense_Tracker_Capstone/
├── main.py
├── expense_manager.py
├── storage.py
├── reports.py
├── utils.py
├── expenses.csv
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

1. Make sure Python 3 is installed on your computer.
2. Open a terminal.
3. Move into the project folder:

```bash
cd ~/Documents/Expense_Tracker_Capstone
```

No extra packages are required because this project uses only the Python
standard library.

## How to Run

Run the application with:

```bash
python main.py
```

If your computer uses `python3` instead of `python`, run:

```bash
python3 main.py
```

## Sample Output

```text
==================================
      EXPENSE TRACKER
==================================
1. Add Expense
2. View All Expenses
3. Search by Category
4. Show Total Spending
5. Monthly Report
6. Delete Expense
7. Save Data
8. Exit
==================================
Enter your choice (1-8): 1

Add Expense
Enter date (YYYY-MM-DD): 2026-07-01
Enter amount: 12.50
Enter category: Food
Enter description: Lunch
Expense added successfully with ID 1.
```

## Future Improvements

- Add charts for monthly spending trends
- Export reports to a separate CSV file
- Add editing support for existing expenses
- Add budgets for each category
- Add unit tests for all modules
