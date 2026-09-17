"""Streamlit UI for MagangHub AI Assistant."""

import os
import sys

import streamlit as st

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import cv_parser, llm, matcher, pdf_generator, scraper

st.set_page_config(
    page_title="MagangHub AI Assistant",
    page_icon="assets/MagangHub Icon - Colored - 669x1024 - zonalogo.com.png",
    layout="wide",
)

# --- Clean Modern Styling ---
st.markdown("""
<style>
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton button:hover {
        opacity: 0.9;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0284c7;
    }
</style>
""", unsafe_allow_html=True)

# Display logo image and title
col_logo, col_title = st.columns([1, 10])
with col_logo:
    if os.path.exists("assets/MagangHub Icon - Colored - 669x1024 - zonalogo.com.png"):
        st.image("assets/MagangHub Icon - Colored - 669x1024 - zonalogo.com.png", width=60)
with col_title:
    st.markdown("### MagangHub AI Assistant")

st.markdown("Optimize your internship applications with AI-powered CV tailoring and cover letters.")

# --- Inputs ---
input_mode = st.radio("Input mode", ["Paste job description text", "MagangHub / job URL"], horizontal=True)

if input_mode == "Paste job description text":
    job_input = st.text_area("Job description", height=200, placeholder="Paste the full job description here...")
else:
    job_input = st.text_input("Job URL", placeholder="https://maganghub.kemnaker.go.id/...")

uploaded_cv = st.file_uploader("Upload CV (PDF)", type=["pdf"])

language = st.selectbox("Cover Letter Language", ["Bahasa Indonesia", "English"])

if st.button("Analyze & Generate", type="primary"):
    if not job_input:
        st.warning("Please enter a job description or URL.")
        st.stop()

    if not uploaded_cv:
        st.warning("Please upload your CV PDF.")
        st.stop()

    try:
        with st.spinner("Reading job post..."):
            job_text = scraper.extract_job_text(job_input)
            if not job_text:
                st.error("Could not read job text.")
                st.stop()

        with st.spinner("Extracting job info with Gemini..."):
            job_info = matcher.extract_job_info(job_text)

        with st.spinner("Reading CV..."):
            cv_text = cv_parser.parse_pdf(uploaded_cv.read())

        with st.spinner("Scoring match..."):
            match_result = matcher.match_cv_to_job(job_info, cv_text)

        # --- Results ---
        st.subheader("Job Details")
        st.write(f"**{job_info.get('title', 'Unknown title')}** at {job_info.get('company', 'Unknown company')}")
        st.write(f"Location: {job_info.get('location') or '-'}")
        st.write(f"Type: {job_info.get('job_type') or '-'}")

        st.subheader("Match Score")
        score = match_result.get("match_score", 0)
        st.metric("Score", f"{score}/100")
        st.progress(score / 100)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Matched Skills**")
            for skill in match_result.get("matched_skills", []):
                st.markdown(f"- ✅ {skill}")
        with col2:
            st.markdown("**Missing Skills**")
            for skill in match_result.get("missing_skills", []):
                st.markdown(f"- ⚠️ {skill}")

        with st.expander("See full gap analysis"):
            st.markdown("**Strengths**")
            for s in match_result.get("strengths", []):
                st.markdown(f"- {s}")
            st.markdown("**Gaps**")
            for g in match_result.get("gaps", []):
                st.markdown(f"- {g}")

        with st.spinner("Generating tailored CV..."):
            tailored_cv = matcher.generate_tailored_cv(job_info, cv_text)

        with st.spinner("Generating cover letter..."):
            cover_letter = matcher.generate_cover_letter(job_info, cv_text, language)

        st.subheader("Tailored CV Summary")
        st.text_area("Copy this into your CV", tailored_cv, height=250)

        st.subheader("Cover Letter")
        st.text_area("Copy this into your application", cover_letter, height=350)

    except llm.RateLimitError as e:
        st.error("⏳ Gemini rate limit hit")
        st.warning(
            "The free Gemini API quota was exceeded. Wait ~1 minute and try again, "
            "or switch to a paid API key / different model in your `.env` file."
        )
        st.info(str(e))
    except Exception as e:
        st.error(f"Error: {e}")
        raise

st.divider()
st.markdown("Built with Streamlit + Gemini · [GitHub](https://github.com/albaruzz/maganghub-ai-assistant)")
