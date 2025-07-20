import pandas as pd
import sqlite3
import faiss
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from extractors.nlp_parser import extract_skills  # skill extractor

# Paths
DATA_PATH = "data/jobs.csv"
DB_PATH = "data/jobs.db"
FAISS_INDEX_PATH = "data/job_index.faiss"

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Step 1: Load dataset
df = pd.read_csv(DATA_PATH)

# Sanity check
if 'job_title' not in df.columns or 'description_text' not in df.columns:
    raise Exception("Dataset must have 'job_title' and 'description_text' columns")

df = df[['job_title', 'company_name', 'location', 'description_text']].dropna()

# Step 2: Generate embeddings and extract skills
print("Generating embeddings and extracting skills...")
descriptions = df['description_text'].tolist()
embeddings = model.encode(descriptions, show_progress_bar=True)
skills_list = [extract_skills(desc) for desc in descriptions]

# Step 3: Save to SQLite with job_skills
print("Saving job info to SQLite...")
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS jobs")
cursor.execute("""
CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT,
    company_name TEXT,
    location TEXT,
    description_text TEXT,
    job_skills TEXT
)
""")

for i, row in df.iterrows():
    cursor.execute("""
        INSERT INTO jobs (job_title, company_name, location, description_text, job_skills)
        VALUES (?, ?, ?, ?, ?)
    """, (row['job_title'], row['company_name'], row['location'], row['description_text'], json.dumps(skills_list[i])))

conn.commit()
conn.close()

# Step 4: Save FAISS index
print("Saving FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))
faiss.write_index(index, FAISS_INDEX_PATH)

print("✅ Job index built and saved!")
