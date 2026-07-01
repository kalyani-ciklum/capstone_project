"""Agent logic for routing user requests to RAG and tools."""

import re

from reflection import reflect_on_answer
from tools import (
    check_expense,
    flag_expense as tool_flag_expense,
    run_evaluation as tool_run_evaluation,
    save_feedback as tool_save_feedback,
    search_policy,
    summarize_policy as tool_summarize_policy,
)


class ExpenseAgent:
    """A simple agentic assistant for expense policy questions."""

    def answer_question(self, question):
        """Answer a policy question using retrieved policy context."""
        intent = self._detect_intent(question)

        if intent == "evaluation":
            evaluation = self.run_evaluation()
            return {
                "answer": (
                    f"Evaluation complete. Passed {evaluation['passed']} "
                    f"out of {evaluation['total']} questions "
                    f"({evaluation['percentage']:.2f}%)."
                ),
                "tool_calls": ["run_evaluation()"],
                "sources": [],
                "reflection": reflect_on_answer(question, "Evaluation run.", []),
            }

        if intent == "summary":
            policy_name = self._extract_policy_name(question)
            return self.summarize_policy(policy_name)

        if intent == "flag":
            expense_id, reason = self._extract_flag_details(question)
            return self.flag_expense(expense_id, reason)

        expense_details = self._extract_expense_details(question)
        if expense_details:
            return self.check_expense_claim(
                expense_details["amount"],
                expense_details["category"],
                expense_details["description"],
            )

        policy_result = search_policy(question)
        sources = policy_result["results"]
        context_enough = bool(sources and sources[0]["score"] > 0.05)
        answer = self._compose_policy_answer(question, sources, context_enough)
        reflection = reflect_on_answer(question, answer, sources)

        return {
            "answer": answer,
            "tool_calls": [f"search_policy({question!r})"],
            "sources": sources,
            "reflection": reflection,
        }

    def check_expense_claim(self, amount, category, description):
        """Check whether an expense claim is allowed."""
        result = check_expense(amount, category, description)
        status = result["status"]
        reason = result["reason"]
        policy_note = result["policy_note"]

        answer = (
            f"Decision: {status}.\n"
            f"Reason: {reason}\n"
            f"Policy basis: {policy_note}"
        )

        reflection = reflect_on_answer(
            f"{category} expense of {amount:.2f} INR: {description}",
            answer,
            result["sources"],
        )

        return {
            "answer": answer,
            "tool_calls": [
                "check_expense("
                f"amount={amount:.2f}, category={category!r}, "
                f"description={description!r})"
            ],
            "sources": result["sources"],
            "reflection": reflection,
        }

    def summarize_policy(self, policy_name):
        """Summarize a named policy document."""
        result = tool_summarize_policy(policy_name)
        answer = result["summary"]
        reflection = reflect_on_answer(
            f"Summarize {policy_name} policy",
            answer,
            result["sources"],
        )

        return {
            "answer": answer,
            "tool_calls": [f"summarize_policy({policy_name!r})"],
            "sources": result["sources"],
            "reflection": reflection,
        }

    def save_feedback(self, question, answer, rating):
        """Save user feedback through the feedback tool."""
        return tool_save_feedback(question, answer, rating)

    def flag_expense(self, expense_id, reason):
        """Flag an expense for later review."""
        result = tool_flag_expense(expense_id, reason)
        answer = result["message"] + f" Reason: {reason}"
        reflection = reflect_on_answer(
            f"Flag expense {expense_id}",
            answer,
            [],
        )

        return {
            "answer": answer,
            "tool_calls": [
                f"flag_expense(expense_id={expense_id!r}, reason={reason!r})"
            ],
            "sources": [],
            "reflection": reflection,
        }

    def run_evaluation(self):
        """Run the evaluation suite."""
        return tool_run_evaluation()

    def _detect_intent(self, question):
        """Identify the user's broad intent from keywords."""
        text = question.lower()

        if "run evaluation" in text or "evaluate" in text:
            return "evaluation"

        if "summarize" in text or "summary" in text:
            return "summary"

        if "flag" in text and "expense" in text:
            return "flag"

        if "policy" in text and any(
            name in text for name in ("travel", "meal", "reimbursement")
        ):
            return "summary"

        return "question"

    def _extract_policy_name(self, question):
        """Find the policy name mentioned in the question."""
        text = question.lower()
        for policy_name in ("travel", "meal", "reimbursement", "approval"):
            if policy_name in text:
                return policy_name
        return question

    def _extract_expense_details(self, question):
        """Extract amount, category, and description from simple claim text."""
        text = question.lower()
        amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:inr|rs|rupees)?", text)

        claim_words = (
            "claim",
            "reimburse",
            "reimbursement",
            "allowed",
            "expense",
            "worth",
        )

        if not amount_match or not any(word in text for word in claim_words):
            return None

        amount = float(amount_match.group(1))
        category = self._guess_category(text)

        return {
            "amount": amount,
            "category": category,
            "description": question,
        }

    def _guess_category(self, text):
        """Guess an expense category from the user's wording."""
        category_keywords = {
            "meal": ["meal", "lunch", "dinner", "breakfast", "food"],
            "travel": ["taxi", "cab", "flight", "train", "hotel", "travel"],
            "approval": ["approval", "manager"],
            "reimbursement": ["reimburse", "receipt", "claim"],
        }

        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category

        return "general"

    def _extract_flag_details(self, question):
        """Extract an expense ID and reason from a flagging request."""
        expense_id_match = re.search(r"\b(e\d+|\d+)\b", question, re.IGNORECASE)
        if expense_id_match:
            expense_id = expense_id_match.group(1).upper()
        else:
            expense_id = "UNKNOWN"

        reason_match = re.search(
            r"(?:because|for|reason)\s+(.+)$",
            question,
            re.IGNORECASE,
        )
        reason = reason_match.group(1).strip() if reason_match else "Manual review requested."

        return expense_id, reason

    def _compose_policy_answer(self, question, sources, context_enough):
        """Create a grounded answer from retrieved policy chunks."""
        if not context_enough:
            return (
                "I could not find enough policy context to answer confidently. "
                "Please ask about travel, meals, reimbursements, or approvals."
            )

        useful_lines = self._select_relevant_snippets(question, sources)
        selected = useful_lines[:5]
        answer_lines = ["Based on the retrieved expense policy context:"]
        answer_lines.extend(f"- {line}" for line in selected)
        answer_lines.append(
            "Use these rules with the claim amount, category, receipt, "
            "and approval requirements before submitting reimbursement."
        )
        return "\n".join(answer_lines)

    def _select_relevant_snippets(self, question, sources):
        """Pick the most relevant sentences or bullet fragments from sources."""
        question_terms = set(re.findall(r"[a-z0-9]+", question.lower()))
        stop_words = {
            "a",
            "an",
            "and",
            "are",
            "can",
            "for",
            "i",
            "is",
            "of",
            "the",
            "to",
            "what",
            "when",
        }
        question_terms = question_terms.difference(stop_words)
        question_terms = self._expand_query_terms(question_terms)
        preferred_terms = self._preferred_domain_terms(question_terms)
        candidates = []

        for source in sources:
            snippets = re.split(r"\s+-\s+|(?<=[.!?])\s+", source["text"])
            for snippet in snippets:
                cleaned = snippet.strip("- ").strip()
                if len(cleaned.split()) < 4:
                    continue

                snippet_terms = set(re.findall(r"[a-z0-9]+", cleaned.lower()))
                score = len(question_terms.intersection(snippet_terms))
                if preferred_terms and preferred_terms.intersection(snippet_terms):
                    score += 5
                elif preferred_terms:
                    score -= 2

                candidates.append((score, cleaned))

        candidates.sort(key=lambda item: item[0], reverse=True)
        selected = [snippet for score, snippet in candidates if score > 0]

        if selected:
            return selected

        return [source["text"] for source in sources[:3]]

    def _expand_query_terms(self, terms):
        """Add simple related terms to improve local retrieval answers."""
        expanded_terms = set(terms)

        if "meal" in terms or "food" in terms:
            expanded_terms.update(
                {"breakfast", "lunch", "dinner", "reimbursable", "limit"}
            )

        if "reimbursement" in terms or "reimburse" in terms:
            expanded_terms.update({"reimbursable", "claim", "claims"})

        if "maximum" in terms or "limit" in terms:
            expanded_terms.update({"inr", "up", "limit", "above"})

        if "taxi" in terms or "cab" in terms:
            expanded_terms.update({"taxi", "cab", "travel", "business"})

        return expanded_terms

    def _preferred_domain_terms(self, terms):
        """Return domain terms that should be preferred in snippets."""
        if "taxi" in terms or "cab" in terms:
            return {"taxi", "cab"}

        if "meal" in terms or "food" in terms:
            return {"breakfast", "lunch", "dinner", "meal"}

        if "approval" in terms or "manager" in terms:
            return {"approval", "manager", "finance"}

        return set()
