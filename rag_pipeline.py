"""Local RAG pipeline using TF-IDF retrieval with scikit-learn."""

import re
from pathlib import Path

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover - handled at runtime for beginners.
    TfidfVectorizer = None
    cosine_similarity = None


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


class RAGPipeline:
    """Load policy documents, chunk them, and retrieve relevant chunks."""

    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = Path(data_dir)
        self.documents = []
        self.chunks = []
        self.vectorizer = None
        self.matrix = None

    def build_index(self):
        """Build the TF-IDF index from policy chunks."""
        self._ensure_sklearn()
        self.documents = self.load_documents()
        self.chunks = self.chunk_documents(self.documents)

        texts = [chunk["text"] for chunk in self.chunks]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(texts)

    def load_documents(self):
        """Read and clean all Markdown policy files."""
        documents = []

        for path in sorted(self.data_dir.glob("*.md")):
            raw_text = path.read_text(encoding="utf-8")
            clean_text = clean_policy_text(raw_text)
            documents.append(
                {
                    "name": path.stem,
                    "source": path.name,
                    "text": clean_text,
                }
            )

        return documents

    def chunk_documents(self, documents, chunk_size=110, overlap=25):
        """Split documents into overlapping word chunks."""
        chunks = []

        for document in documents:
            words = document["text"].split()
            start = 0
            chunk_id = 1

            while start < len(words):
                end = start + chunk_size
                chunk_words = words[start:end]
                chunks.append(
                    {
                        "source": document["source"],
                        "policy_name": document["name"],
                        "chunk_id": chunk_id,
                        "text": " ".join(chunk_words),
                    }
                )
                chunk_id += 1
                start += chunk_size - overlap

        return chunks

    def retrieve(self, query, top_k=3):
        """Return the top_k most relevant chunks for a query."""
        if self.matrix is None:
            self.build_index()

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        adjusted_scores = self._boost_scores(query, scores)
        ranked_indexes = adjusted_scores.argsort()[::-1][:top_k]

        results = []
        for index in ranked_indexes:
            chunk = self.chunks[index]
            results.append(
                {
                    "source": chunk["source"],
                    "policy_name": chunk["policy_name"],
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "score": float(adjusted_scores[index]),
                }
            )

        return results

    def summarize_policy(self, policy_name):
        """Return a short extractive summary for a named policy."""
        if not self.documents:
            self.documents = self.load_documents()

        normalized_name = normalize_text(policy_name)
        matching_document = None

        for document in self.documents:
            document_name = normalize_text(document["name"])
            if normalized_name in document_name or document_name in normalized_name:
                matching_document = document
                break

        if matching_document is None:
            return {
                "summary": (
                    "Policy not found. Available policies are travel, meal, "
                    "reimbursement, and approval."
                ),
                "sources": [],
            }

        lines = [
            line.strip()
            for line in matching_document["text"].splitlines()
            if line.strip()
        ]
        summary_lines = lines[:8]

        return {
            "summary": "\n".join(summary_lines),
            "sources": [
                {
                    "source": matching_document["source"],
                    "policy_name": matching_document["name"],
                    "chunk_id": 1,
                    "text": "\n".join(summary_lines),
                    "score": 1.0,
                }
            ],
        }

    def _ensure_sklearn(self):
        """Raise a friendly error when scikit-learn is not installed."""
        if TfidfVectorizer is None or cosine_similarity is None:
            raise RuntimeError(
                "scikit-learn is required for TF-IDF retrieval. "
                "Install it with: pip install -r requirements.txt"
            )

    def _boost_scores(self, query, scores):
        """Boost scores when the query clearly matches a policy domain."""
        query_terms = set(normalize_text(query).split())
        adjusted_scores = scores.copy()

        policy_hints = {
            "travel_expense_policy": {
                "travel",
                "taxi",
                "cab",
                "flight",
                "hotel",
                "train",
                "airport",
            },
            "meal_expense_policy": {
                "meal",
                "food",
                "breakfast",
                "lunch",
                "dinner",
            },
            "reimbursement_policy": {
                "reimburse",
                "reimbursement",
                "receipt",
                "claim",
                "payment",
            },
            "approval_policy": {
                "approval",
                "approve",
                "manager",
                "finance",
                "exception",
            },
        }

        for index, chunk in enumerate(self.chunks):
            policy_name = chunk["policy_name"]
            chunk_terms = set(
                normalize_text(f"{policy_name} {chunk['text']}").split()
            )
            shared_terms = query_terms.intersection(chunk_terms)
            adjusted_scores[index] += len(shared_terms) * 0.02

            hint_terms = policy_hints.get(policy_name, set())
            if query_terms.intersection(hint_terms):
                adjusted_scores[index] += 0.25

        return adjusted_scores


def clean_policy_text(text):
    """Normalize Markdown policy text for retrieval."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("##", "\n").replace("#", "\n")
    text = text.replace("- ", "\n- ")
    return text.strip()


def normalize_text(text):
    """Normalize text for simple matching."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


_PIPELINE = None


def get_pipeline():
    """Return a shared RAGPipeline instance."""
    global _PIPELINE

    if _PIPELINE is None:
        _PIPELINE = RAGPipeline()

    return _PIPELINE
