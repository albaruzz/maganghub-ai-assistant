"""Match job to CV and generate outputs."""

import json
from typing import Any

from src import llm


def extract_job_info(job_text: str) -> dict[str, Any]:
    """Use LLM to extract structured job info."""
    prompt = llm.build_extract_job_prompt(job_text)
    raw = llm.call_gemini(prompt, json_mode=True)
    return llm.parse_json_response(raw)


def match_cv_to_job(job_info: dict, cv_text: str) -> dict[str, Any]:
    """Return match score + gaps."""
    prompt = llm.build_match_prompt(job_info, cv_text)
    raw = llm.call_gemini(prompt, json_mode=True)
    return llm.parse_json_response(raw)


def generate_tailored_cv(job_info: dict, cv_text: str) -> str:
    """Generate tailored CV bullets."""
    prompt = llm.build_cv_rewrite_prompt(job_info, cv_text)
    return llm.call_gemini(prompt, json_mode=False)


def generate_cover_letter(job_info: dict, cv_text: str, language: str = "Bahasa Indonesia") -> str:
    """Generate cover letter."""
    prompt = llm.build_cover_letter_prompt(job_info, cv_text, language)
    return llm.call_gemini(prompt, json_mode=False)
