"""Tool functions used by the expense assistant agent."""

import csv
from datetime import datetime
from pathlib import Path

from rag_pipeline import get_pipeline

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
FEEDBACK_FILE = OUTPUTS_DIR / "feedback_log.csv"
FLAGGED_FILE = OUTPUTS_DIR / "flagged_expenses.csv"


def search_policy(query):
    """Search policy documents and return the top 3 relevant chunks."""
    pipeline = get_pipeline()
    results = pipeline.retrieve(query, top_k=3)
    return {"query": query, "results": results}


def check_expense(amount, category, description):
    """Check whether an expense is allowed, not allowed, or needs approval."""
    amount = float(amount)
    category_text = category.lower()
    description_text = description.lower()
    combined_text = f"{category_text} {description_text}"

    policy_result = search_policy(combined_text)
    sources = policy_result["results"]

    if _contains_any(combined_text, ["alcohol", "personal", "fine", "penalty"]):
        return {
            "status": "Not Allowed",
            "reason": (
                "The description includes an item that the policy treats as "
                "non-reimbursable."
            ),
            "policy_note": "Alcohol, personal purchases, fines, and penalties are not reimbursable.",
            "sources": sources,
        }

    if _contains_any(combined_text, ["breakfast"]):
        return _evaluate_limit(amount, 250, 500, "breakfast", sources)

    if _contains_any(combined_text, ["lunch"]):
        return _evaluate_limit(amount, 500, 900, "lunch", sources)

    if _contains_any(combined_text, ["dinner"]):
        return _evaluate_limit(amount, 800, 1200, "dinner", sources)

    if _contains_any(combined_text, ["meal", "food"]):
        return _evaluate_limit(amount, 700, 1200, "meal", sources)

    if _contains_any(combined_text, ["taxi", "cab", "ride"]):
        return _evaluate_limit(amount, 1500, 5000, "taxi travel", sources)

    if _contains_any(combined_text, ["flight", "airfare", "train", "hotel"]):
        return _evaluate_limit(amount, 5000, 25000, "travel", sources)

    if amount > 5000:
        return {
            "status": "Needs Approval",
            "reason": "Any single expense above INR 5000 needs manager approval.",
            "policy_note": "Manager approval is required for expenses above INR 5000.",
            "sources": sources,
        }

    return {
        "status": "Allowed",
        "reason": "The claim is within the general reimbursement threshold.",
        "policy_note": "Submit the claim with a valid receipt and business purpose.",
        "sources": sources,
    }


def summarize_policy(policy_name):
    """Summarize one policy document."""
    pipeline = get_pipeline()
    return pipeline.summarize_policy(policy_name)


def flag_expense(expense_id, reason):
    """Log a flagged expense for later review."""
    _ensure_output_file(FLAGGED_FILE, ["timestamp", "expense_id", "reason"])

    with FLAGGED_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([_timestamp(), expense_id, reason])

    return {
        "message": f"Expense {expense_id} was flagged for review.",
        "expense_id": expense_id,
        "reason": reason,
    }


def save_feedback(question, answer, rating):
    """Save user feedback about an answer."""
    _ensure_output_file(
        FEEDBACK_FILE,
        ["timestamp", "question", "answer", "rating"],
    )

    with FEEDBACK_FILE.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([_timestamp(), question, answer, rating])

    return {"message": "Feedback saved successfully."}


def run_evaluation():
    """Run the evaluation tool."""
    from evaluation import run_evaluation as evaluate

    return evaluate()


def _evaluate_limit(amount, allowed_limit, approval_limit, expense_type, sources):
    """Evaluate an amount against allowed and approval thresholds."""
    if amount <= allowed_limit:
        return {
            "status": "Allowed",
            "reason": (
                f"The {expense_type} amount is within the INR "
                f"{allowed_limit:.0f} automatic reimbursement limit."
            ),
            "policy_note": (
                f"{expense_type.title()} expenses up to INR "
                f"{allowed_limit:.0f} are allowed with a receipt."
            ),
            "sources": sources,
        }

    if amount <= approval_limit:
        return {
            "status": "Needs Approval",
            "reason": (
                f"The {expense_type} amount is above the normal INR "
                f"{allowed_limit:.0f} limit but below the exception limit."
            ),
            "policy_note": (
                "Manager approval and a written business justification are "
                "required before reimbursement."
            ),
            "sources": sources,
        }

    return {
        "status": "Not Allowed",
        "reason": (
            f"The {expense_type} amount is above the INR "
            f"{approval_limit:.0f} exception limit."
        ),
        "policy_note": (
            "Claims above the exception limit are not reimbursed unless Finance "
            "grants a special exception."
        ),
        "sources": sources,
    }


def _contains_any(text, keywords):
    """Return True when any keyword appears in text."""
    return any(keyword in text for keyword in keywords)


def _ensure_output_file(path, headers):
    """Create an output CSV with headers if it does not exist."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)


def _timestamp():
    """Return a readable timestamp for logs."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
