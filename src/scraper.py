"""MagangHub job post scraper."""

import re
import requests
from bs4 import BeautifulSoup


def fetch_html(url: str, timeout: int = 20) -> str:
    """Fetch raw HTML from a URL."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def clean_text(html: str) -> str:
    """Convert HTML to readable plain text."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style/nav/footer noise
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Collapse blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def extract_job_text(url_or_text: str) -> str:
    """Return cleaned job description text from a MagangHub URL or raw pasted text."""
    if is_maganghub_url(url_or_text):
        html = fetch_html(url_or_text)
        return clean_text(html)
    return url_or_text.strip()


def is_maganghub_url(url: str) -> bool:
    """Basic guard to ensure URL looks like a MagangHub page."""
    return bool(re.search(r"maganghub\.id", url, re.IGNORECASE))
