"""Optional Gemini LLM client with simple retry handling."""

import logging
import os
import time

try:
    from dotenv import load_dotenv
except ImportError:  # Allows the local RAG app to run before installation.
    load_dotenv = None

try:
    from google import genai
except ImportError:  # Allows mentor review without a Gemini dependency.
    genai = None


logger = logging.getLogger(__name__)
DEFAULT_MODEL = "gemini-2.5-flash"


def load_environment():
    """Load environment variables from .env when python-dotenv is installed."""
    if load_dotenv is not None:
        load_dotenv()


def is_llm_enabled():
    """Return True when Gemini dependencies and API key are available."""
    load_environment()
    return genai is not None and bool(os.getenv("GEMINI_API_KEY"))


def ask_llm(prompt, model=None, retry_count=3, wait_time=15):
    """Ask Gemini for a response, retrying quota errors."""
    load_environment()

    if genai is None:
        return (
            "LLM client is unavailable. Install dependencies with "
            "`pip install -r requirements.txt`."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "LLM is not configured. Add GEMINI_API_KEY to your .env file."

    client = genai.Client(api_key=api_key)
    selected_model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    for attempt in range(retry_count):
        try:
            response = client.models.generate_content(
                model=selected_model,
                contents=prompt,
            )
            return response.text
        except Exception as exc:
            if "429" in str(exc):
                logger.warning(
                    "Quota exceeded on attempt %s. Retrying in %ss.",
                    attempt + 1,
                    wait_time,
                )
                print(f"Quota exceeded. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

    return "LLM request failed after retries."
