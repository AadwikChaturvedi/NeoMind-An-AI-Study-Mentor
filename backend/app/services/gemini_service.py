"""
services/gemini_service.py
----------------------------
Wraps all calls to the Gemini API. Keeping this in one place means
the API key, model choice, and system prompt only live here —
routes/mentor.py just calls ask_mentor() and doesn't know how it works.

Uses the `google-genai` SDK — the current, actively maintained one.
(The older `google-generativeai` package is deprecated as of 2025.)
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

# .env lives at the project root (one level up from backend/). This call
# is harmless if main.py already loaded it — python-dotenv doesn't
# overwrite variables that are already set. It just makes this module
# work correctly even if something imports it before main.py runs.
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

SYSTEM_PROMPT = """You are NeoMind AI, a productivity mentor for students preparing for competitive exams.

Responsibilities:
- motivate students
- improve focus
- suggest study strategies
- give concise answers"""

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

_client: genai.Client | None = None


class GeminiServiceError(Exception):
    """Raised whenever the Gemini API can't fulfill a request. Carries
    an HTTP-style status_code so routes/mentor.py can turn it directly
    into a clean response instead of guessing what went wrong."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _get_client() -> genai.Client:
    """Lazily creates the Gemini client. This means a missing API key
    only fails when /mentor/chat is actually called, not at import
    time — which would otherwise crash the whole app on startup."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY is not set. Add it to backend/.env.",
                status_code=500,
            )
        _client = genai.Client(api_key=api_key)
    return _client


def ask_mentor(message: str) -> str:
    """Sends a student's message to Gemini with the mentor system
    prompt and returns the reply text. Raises GeminiServiceError on
    any failure (missing key, rate limit, network issue, etc.) —
    callers don't need to know which SDK exception means what."""
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=message,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
    except genai_errors.APIError as e:
        if e.code == 429:
            raise GeminiServiceError(
                "Gemini is rate-limiting requests right now. Try again shortly.", status_code=429
            ) from e
        if e.code in (401, 403):
            raise GeminiServiceError(
                "Gemini rejected the API key. Check GEMINI_API_KEY in backend/.env.", status_code=500
            ) from e
        if e.code in (500, 503, 504):
            raise GeminiServiceError(
                "Gemini's service is temporarily unavailable. Try again shortly.", status_code=502
            ) from e
        raise GeminiServiceError(f"Gemini API error: {e.message}", status_code=502) from e
    except Exception as e:
        # Covers network failures, timeouts, etc. that happen before
        # the API even responds.
        raise GeminiServiceError(f"Couldn't reach Gemini: {e}", status_code=502) from e

    if not response.text:
        raise GeminiServiceError("Gemini returned an empty response.", status_code=502)

    return response.text
