import re
from pathlib import Path
from typing import Dict, List

from docx import Document
from PyPDF2 import PdfReader


COMMON_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "node.js",
    "fastapi",
    "flask",
    "django",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "machine learning",
    "deep learning",
    "nlp",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "git",
    "html",
    "css",
    "rest api",
    "excel",
    "power bi",
    "tableau",
}

EDUCATION_KEYWORDS = [
    "b.tech",
    "bachelor",
    "bachelors",
    "b.sc",
    "bca",
    "m.tech",
    "master",
    "masters",
    "m.sc",
    "mca",
    "mba",
    "phd",
    "diploma",
]


def extract_resume_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf_text(file_path)

    if suffix == ".docx":
        return _extract_docx_text(file_path)

    raise ValueError("Unsupported file format.")


def _extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages)


def _extract_docx_text(file_path: Path) -> str:
    document = Document(str(file_path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def parse_resume_details(text: str, fallback_name: str) -> Dict[str, object]:
    normalized = _normalize_spaces(text)

    return {
        "name": _extract_candidate_name(text, fallback_name),
        "skills": _extract_skills(normalized),
        "education": _extract_education(normalized),
        "experience": _extract_experience(normalized),
        "keywords": _extract_keywords(normalized),
    }


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_candidate_name(text: str, fallback_name: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        first_line = re.sub(r"[^A-Za-z .'-]", "", lines[0]).strip()
        words = first_line.split()
        if 1 <= len(words) <= 4:
            return first_line.title()

    cleaned_fallback = re.sub(r"[_\-]+", " ", fallback_name).strip()
    return cleaned_fallback.title() or "Unknown Candidate"


def _extract_skills(text: str) -> List[str]:
    lower_text = text.lower()
    found = []

    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, lower_text):
            found.append(skill.title() if skill != "node.js" else "Node.js")

    return sorted(set(found))


def _extract_education(text: str) -> List[str]:
    lower_text = text.lower()
    education = []

    for keyword in EDUCATION_KEYWORDS:
        if keyword in lower_text:
            education.append(keyword.upper() if "." in keyword else keyword.title())

    return sorted(set(education))


def _extract_experience(text: str) -> str:
    patterns = [
        r"(\d+\+?\s*(?:years|year|yrs|yr)\s+(?:of\s+)?experience)",
        r"experience\s*(?:of)?\s*(\d+\+?\s*(?:years|year|yrs|yr))",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return "Not clearly mentioned"


def _extract_keywords(text: str) -> List[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#.-]{2,}\b", text.lower())
    blocked = {
        "and",
        "the",
        "for",
        "with",
        "from",
        "this",
        "that",
        "are",
        "was",
        "you",
        "your",
        "resume",
        "candidate",
    }
    keywords = [word for word in words if word not in blocked]
    frequency = {}

    for word in keywords:
        frequency[word] = frequency.get(word, 0) + 1

    ranked = sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    return [word for word, _ in ranked[:20]]
