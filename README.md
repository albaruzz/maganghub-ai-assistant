# MagangHub AI Assistant

AI-powered job application assistant for [MagangHub](https://maganghub.kemnaker.go.id) Indonesia internships.

Scrapes a MagangHub job post, parses your CV, scores how well you match, and generates a tailored CV + cover letter.

## Features

- Paste MagangHub job URL → auto-extract title, company, requirements, skills
- Upload CV PDF → extract experience, projects, skills
- Match score + missing skills gap analysis
- Generate tailored CV bullet points
- Generate formal cover letter (Bahasa Indonesia / English)

## Tech Stack

- Python 3.11+
- Streamlit (UI)
- `requests` + `BeautifulSoup` (web scraping)
- `pdfplumber` (CV parsing)
- Google Gemini API (LLM)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Run

```bash
streamlit run app.py
```

Open the URL shown in terminal (usually http://localhost:8501).

## Project Structure

```
.
├── app.py              # Streamlit UI
├── src/
│   ├── scraper.py      # MagangHub job scraper
│   ├── cv_parser.py    # PDF CV parser
│   ├── llm.py          # Gemini client + prompts
│   └── matcher.py      # Match score + generator
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT
