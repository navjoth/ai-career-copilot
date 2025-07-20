import os
import fitz  # PyMuPDF
import faiss
import sqlite3
import json   # ✅ <-- Add this
from sentence_transformers import SentenceTransformer
from extractors.resume_parser import extract_resume_text
from extractors.nlp_parser import extract_skills
from tqdm import tqdm


# === CONFIG ===
RESUME_PATH = "data/resume_2.pdf"
FAISS_INDEX_PATH = "data/job_index.faiss"
SQLITE_DB_PATH = "data/jobs.db"
TOP_K = 3

# === LOAD EMBEDDING MODEL ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# === EXTRACT TEXT & SKILLS FROM RESUME ===
print("🔍 Parsing resume...")
resume_text = extract_resume_text(RESUME_PATH)
resume_skills = extract_skills(resume_text)

# === EMBED RESUME ===
print("📐 Embedding resume...")
resume_embedding = model.encode([resume_text])[0]

# === LOAD FAISS INDEX ===
print("📦 Loading FAISS index...")
index = faiss.read_index(FAISS_INDEX_PATH)

# === SEARCH TOP JOBS ===
print("📊 Searching for top job matches...")
D, I = index.search(resume_embedding.reshape(1, -1), TOP_K)
top_indices = I[0]
similarities = D[0]

# === CONNECT TO JOB DATABASE ===
conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()

print("\n--- Top Job Matches ---\n")
for rank, (idx, score) in enumerate(zip(top_indices, similarities), 1):
    cursor.execute("SELECT job_title, company_name, location, description_text, job_skills FROM jobs WHERE job_id = ?", (int(idx),))
    row = cursor.fetchone()
    if row:
        title, company, location, description, job_skills_json = row
        job_skills = json.loads(job_skills_json) if job_skills_json else []
        missing_skills = sorted(set(job_skills) - set(resume_skills))

        print(f"Rank {rank}: {title} at {company}")
        print(f"Location: {location}")
        print(f"Similarity Score: {score:.2f}")
        print(f"Missing Skills: {missing_skills if missing_skills else '✅ All skills matched!'}")
        print("-" * 50)

conn.close()
