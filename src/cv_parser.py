"""CV PDF parser."""

import io
import re
import pdfplumber


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_skills(text: str) -> list[str]:
    """Naive skill extractor: looks for common tech keywords."""
    # This is a placeholder; LLM will do the real extraction.
    common = [
        "python", "java", "javascript", "typescript", "sql",
        "tensorflow", "pytorch", "machine learning", "deep learning",
        "nlp", "llm", "genai", "streamlit", "fastapi", "flask",
        "git", "docker", "aws", "gcp", "azure", "linux",
        "react", "node.js", "pandas", "numpy", "scikit-learn",
    ]
    found = []
    lower = text.lower()
    for skill in common:
        if re.search(rf"\b{re.escape(skill)}\b", lower):
            found.append(skill)
    return found
