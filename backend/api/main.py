from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from extractors.resume_parser import extract_resume_text
from extractors.nlp_parser import extract_skills
import faiss
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import json

app = FastAPI()

# === CORS CONFIGURATION (allow frontend to talk to backend) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === CONSTANT PATHS ===
FAISS_INDEX_PATH = "data/job_index.faiss"
SQLITE_DB_PATH = "data/jobs.db"

# === LOAD MODEL + INDEX + DB CONNECTION ===
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(FAISS_INDEX_PATH)
conn = sqlite3.connect(SQLITE_DB_PATH)

# === MATCHING ENDPOINT ===
@app.post("/match")
async def match_resume(file: UploadFile = File(...)):
    content = await file.read()

    # Save the uploaded resume temporarily
    with open("temp_resume.pdf", "wb") as f:
        f.write(content)

    # Extract text and skills from the resume
    resume_text = extract_resume_text("temp_resume.pdf")
    resume_skills = extract_skills(resume_text)

    # Generate embedding from resume text
    resume_embedding = model.encode([resume_text])[0]
    D, I = index.search(np.array([resume_embedding]), k=3)

    # Fetch top job matches from database
    results = []
    cursor = conn.cursor()
    for idx, score in zip(I[0], D[0]):
        cursor.execute("SELECT job_title, company_name, location, description_text FROM jobs WHERE job_id = ?", (int(idx),))
        row = cursor.fetchone()
        if row:
            title, company, location, description = row
            job_skills = extract_skills(description)
            missing = sorted(set(job_skills) - set(resume_skills))

            results.append({
                "title": title,
                "company": company,
                "location": location,
                "score": float(score),
                "missing_skills": missing
            })

    return {"matches": results}



from pydantic import BaseModel
from fastapi import HTTPException

class JobPost(BaseModel):
    title: str
    company: str
    location: str
    description: str

@app.post("/add_job")
def add_job(job: JobPost):
    # Reconnect to SQLite inside the request thread
    local_conn = sqlite3.connect(SQLITE_DB_PATH)
    local_cursor = local_conn.cursor()

    # 1. Encode job description
    job_text = f"{job.title} at {job.company}, {job.location}. {job.description}"
    job_vector = model.encode([job_text]).astype("float32")

    # 2. Add to FAISS index and save
    index.add(job_vector)
    faiss.write_index(index, FAISS_INDEX_PATH)

    # 3. Insert into database
    try:
        local_cursor.execute(
            "INSERT INTO jobs (job_title, company_name, location, description_text) VALUES (?, ?, ?, ?)",
            (job.title, job.company, job.location, job.description)
        )
        local_conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert job into database: {str(e)}")
    finally:
        local_conn.close()

    return {"message": "✅ Job added successfully!"}
