"""Self-reflection scoring for assistant answers."""

import re


def reflect_on_answer(question, answer, sources):
    """Score an answer for relevance, groundedness, and clarity."""
    source_text = " ".join(source.get("text", "") for source in sources)

    relevance_score = _overlap_score(question, answer)
    groundedness_score = _overlap_score(answer, source_text) if sources else 5
    clarity_score = _clarity_score(answer)

    return {
        "relevance": {
            "score": relevance_score,
            "explanation": _explain_score(relevance_score, "the user question"),
        },
        "groundedness": {
            "score": groundedness_score,
            "explanation": _explain_score(
                groundedness_score,
                "retrieved policy context",
            ),
        },
        "clarity": {
            "score": clarity_score,
            "explanation": _explain_score(clarity_score, "clear wording"),
        },
        "improvement_suggestion": _suggest_improvement(
            relevance_score,
            groundedness_score,
            clarity_score,
        ),
    }


def _overlap_score(text_a, text_b):
    """Calculate a simple word-overlap score from 1 to 10."""
    words_a = _important_words(text_a)
    words_b = _important_words(text_b)

    if not words_a or not words_b:
        return 5

    overlap = words_a.intersection(words_b)
    ratio = len(overlap) / max(1, len(words_a))
    return max(1, min(10, round(4 + ratio * 6)))


def _clarity_score(answer):
    """Score clarity using length and structure heuristics."""
    if not answer.strip():
        return 1

    word_count = len(answer.split())
    has_structure = any(marker in answer for marker in ("-", "Decision:", "\n"))

    if 20 <= word_count <= 180 and has_structure:
        return 9
    if 10 <= word_count <= 220:
        return 7
    return 5


def _important_words(text):
    """Extract meaningful words for scoring."""
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
        "on",
        "or",
        "the",
        "to",
        "what",
        "when",
        "with",
    }
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    return {word for word in words if word not in stop_words}


def _explain_score(score, focus):
    """Create a short explanation for a score."""
    if score >= 8:
        return f"The answer is strong for {focus}."
    if score >= 6:
        return f"The answer is acceptable but could improve for {focus}."
    return f"The answer may be weak for {focus}."


def _suggest_improvement(relevance, groundedness, clarity):
    """Suggest one improvement based on the lowest score."""
    lowest = min(relevance, groundedness, clarity)

    if lowest == groundedness:
        return "Add more direct policy wording or cite a stronger policy chunk."
    if lowest == relevance:
        return "Address the user's exact category, amount, and condition more directly."
    return "Make the response shorter and use clearer bullet points."
