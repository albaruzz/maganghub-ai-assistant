"""Gemini LLM client and prompt builders using google-genai SDK."""

import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from project root regardless of cwd
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))


class RateLimitError(RuntimeError):
    """Raised when the Gemini API quota / rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


def _get_client() -> genai.Client:
    """Create a Gemini client from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set. Copy .env.example to .env and fill it.")
    return genai.Client(api_key=api_key)


def get_model_name() -> str:
    return os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")


def call_gemini(
    prompt: str,
    json_mode: bool = False,
    temperature: float = 0.3,
    max_retries: int = 3,
) -> str:
    """Send prompt to Gemini and return text. Retry on 429 quota errors."""
    client = _get_client()
    model = get_model_name()

    config = types.GenerateContentConfig(
        temperature=temperature,
        response_mime_type="application/json" if json_mode else "text/plain",
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as exc:
            last_error = exc
            error_message = str(exc).lower()
            # Retry on quota (429) and temporary overload (503)
            if any(k in error_message for k in ("429", "quota", "rate limit", "503", "unavailable")):
                wait = 2 ** attempt * 15  # 15s, 30s, 60s
                time.sleep(wait)
                continue
            raise
    # Surface quota/rate-limit failures with a dedicated exception so the UI can notify the user.
    if last_error and any(k in str(last_error).lower() for k in ("429", "quota", "rate limit")):
        raise RateLimitError(
            f"Gemini API rate limit exceeded after {max_retries} retries. "
            "Wait a minute or check your plan/billing at https://ai.google.dev/gemini-api/docs/rate-limits"
        ) from last_error
    raise RuntimeError(f"Gemini API failed after {max_retries} retries: {last_error}")


def parse_json_response(text: str) -> dict[str, Any]:
    """Clean and parse JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def build_extract_job_prompt(job_text: str) -> str:
    return f"""You are an expert at parsing job postings.
Extract the following fields from the job description below.
Return ONLY valid JSON with these keys:
- title (string)
- company (string)
- location (string or null)
- job_type (string or null, e.g. "Internship", "Full-time")
- requirements (list of strings)
- responsibilities (list of strings)
- skills (list of strings)
- description (string, short summary)

Job description:
---
{job_text[:12000]}
---
"""


def build_match_prompt(job_info: dict, cv_text: str) -> str:
    return f"""You are a career coach helping a junior developer apply for an internship.
Given the job information and the CV text below, produce ONLY valid JSON with:
- match_score (integer 0-100)
- matched_skills (list of strings)
- missing_skills (list of strings)
- gaps (list of strings, what the candidate should improve)
- strengths (list of strings)

Job information:
{json.dumps(job_info, ensure_ascii=False, indent=2)}

CV text:
---
{cv_text[:12000]}
---
"""


def build_cv_rewrite_prompt(job_info: dict, cv_text: str) -> str:
    return f"""Rewrite the CV summary/bullet points below to better match this internship.
Keep facts truthful. Do not invent experience. Highlight relevant skills and projects.
Return ONLY plain text (not JSON), ready to copy into a CV.

Job information:
{json.dumps(job_info, ensure_ascii=False, indent=2)}

CV text:
---
{cv_text[:12000]}
---
"""


def build_cover_letter_prompt(job_info: dict, cv_text: str, language: str = "Bahasa Indonesia") -> str:
    return f"""Write a formal cover letter in {language} for the internship below.
Use information from the CV. Keep it concise, polite, and professional.
Return ONLY plain text (not JSON).

Job information:
{json.dumps(job_info, ensure_ascii=False, indent=2)}

CV text:
---
{cv_text[:12000]}
---
"""
