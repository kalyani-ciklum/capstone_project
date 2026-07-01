"""Evaluation runner for the AI Agentic Expense Assistant."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EVAL_FILE = BASE_DIR / "eval" / "test_questions.json"


def run_evaluation():
    """Run keyword-based evaluation against sample questions."""
    from agent import ExpenseAgent

    test_cases = _load_test_cases()
    agent = ExpenseAgent()
    results = []

    for test_case in test_cases:
        question = test_case["question"]
        expected_keywords = [
            keyword.lower() for keyword in test_case["expected_keywords"]
        ]
        response = agent.answer_question(question)
        answer = response["answer"].lower()
        missing_keywords = [
            keyword for keyword in expected_keywords if keyword not in answer
        ]
        passed = not missing_keywords

        results.append(
            {
                "question": question,
                "passed": passed,
                "missing_keywords": missing_keywords,
                "answer": response["answer"],
            }
        )

    passed_count = sum(1 for result in results if result["passed"])
    total = len(results)
    percentage = (passed_count / total * 100) if total else 0

    return {
        "passed": passed_count,
        "total": total,
        "percentage": percentage,
        "results": results,
    }


def _load_test_cases():
    """Load test questions from JSON."""
    with EVAL_FILE.open("r", encoding="utf-8") as json_file:
        return json.load(json_file)
