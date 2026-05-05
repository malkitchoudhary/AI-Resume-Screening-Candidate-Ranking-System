# AI Resume Screening & Candidate Ranking System

A FastAPI based project that uploads PDF/DOCX resumes, extracts resume text, compares every resume with a job description using TF-IDF and cosine similarity, then ranks candidates by match percentage.

## Features

- Multiple PDF/DOCX resume upload
- Job description input
- Resume text extraction
- Skills, education, experience, and keyword extraction
- NLP preprocessing with stopword removal and spaCy support
- TF-IDF + cosine similarity scoring
- Candidate ranking table
- Top 3 candidates section
- Matched keyword chips
- Friendly frontend with HTML, CSS, and JavaScript
- Invalid file and empty input handling

## Project Structure

```text
AI Resume Screening/
  backend/
    app.py
    matcher.py
    resume_parser.py
    uploads/
  frontend/
    index.html
    script.js
    style.css
  requirements.txt
  README.md
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

The spaCy model improves lemmatization. The app still runs without it because the backend has a safe fallback.

## Run

```bash
uvicorn backend.app:app --reload
```

Open this URL in your browser:

```text
http://127.0.0.1:8000
```

## API

```text
POST /api/rank
```

Form fields:

- `job_description`: job description text
- `resumes`: one or more PDF/DOCX files

## Notes

- Uploaded resumes are stored temporarily in `backend/uploads` and removed after processing.
- Matching scores are calculated as percentages from cosine similarity.
- Candidate name extraction uses a simple heuristic from the resume text or file name.
