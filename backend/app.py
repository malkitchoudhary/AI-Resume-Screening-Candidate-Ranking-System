from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_DIR = Path("/tmp/uploads") if Path("/tmp").exists() else BASE_DIR / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI Resume Screening & Candidate Ranking System",
    description="Upload resumes, compare them with a job description, and rank candidates.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/style.css")
def serve_stylesheet():
    return FileResponse(FRONTEND_DIR / "style.css")


@app.get("/script.js")
def serve_script():
    return FileResponse(FRONTEND_DIR / "script.js")


@app.post("/api/rank")
async def rank_resumes(
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...),
):
    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    if not resumes:
        raise HTTPException(status_code=400, detail="Please upload at least one resume.")

    parsed_candidates = []
    errors = []

    from .matcher import rank_candidates
    from .resume_parser import extract_resume_text, parse_resume_details

    for resume in resumes:
        suffix = Path(resume.filename or "").suffix.lower()
        if suffix not in {".pdf", ".docx"}:
            errors.append(
                {
                    "file": resume.filename,
                    "error": "Invalid file type. Only PDF and DOCX files are supported.",
                }
            )
            continue

        saved_path = UPLOAD_DIR / Path(resume.filename).name

        try:
            content = await resume.read()
            saved_path.write_bytes(content)
            text = extract_resume_text(saved_path)

            if not text.strip():
                errors.append({"file": resume.filename, "error": "No readable text found."})
                continue

            details = parse_resume_details(text, fallback_name=saved_path.stem)
            parsed_candidates.append(
                {
                    "file_name": resume.filename,
                    "text": text,
                    "details": details,
                }
            )
        except Exception as exc:
            errors.append({"file": resume.filename, "error": str(exc)})
        finally:
            try:
                saved_path.unlink(missing_ok=True)
            except OSError:
                pass

    if not parsed_candidates:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "No valid resumes could be processed.",
                "errors": errors,
            },
        )

    ranked_candidates = rank_candidates(job_description, parsed_candidates)

    return {
        "total_processed": len(ranked_candidates),
        "top_candidates": ranked_candidates[:3],
        "candidates": ranked_candidates,
        "errors": errors,
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
