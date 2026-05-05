import re
from typing import Dict, List

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import spacy
except ImportError:
    spacy = None


def _load_nlp():
    if spacy is None:
        return None

    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        return spacy.blank("en")


NLP = _load_nlp()


def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#. ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return ""

    if NLP is not None:
        doc = NLP(text)
        tokens = []
        for token in doc:
            lemma = token.lemma_.strip() if token.lemma_ else token.text
            if lemma and lemma not in ENGLISH_STOP_WORDS and len(lemma) > 1:
                tokens.append(lemma)
        return " ".join(tokens)

    words = text.split()
    return " ".join(word for word in words if word not in ENGLISH_STOP_WORDS and len(word) > 1)


def rank_candidates(job_description: str, candidates: List[Dict[str, object]]) -> List[Dict[str, object]]:
    documents = [preprocess_text(job_description)]
    documents.extend(preprocess_text(candidate["text"]) for candidate in candidates)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(documents)
    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    ranked = []
    job_terms = _important_terms(job_description)

    for index, candidate in enumerate(candidates):
        details = candidate["details"]
        resume_terms = set(_important_terms(candidate["text"]))
        matched_keywords = sorted(job_terms.intersection(resume_terms))

        ranked.append(
            {
                "rank": 0,
                "candidate_name": details["name"],
                "file_name": candidate["file_name"],
                "score": round(float(scores[index]) * 100, 2),
                "matched_keywords": matched_keywords[:25],
                "skills": details["skills"],
                "education": details["education"],
                "experience": details["experience"],
                "keywords": details["keywords"],
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)

    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank

    return ranked


def _important_terms(text: str) -> set:
    cleaned = preprocess_text(text)
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#.]{2,}\b", cleaned)
    return {word for word in words if word not in ENGLISH_STOP_WORDS}
