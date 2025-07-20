import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from extractors.nlp_parser import extract_skills
from extractors.resume_parser import extract_resume_text

model = SentenceTransformer('all-MiniLM-L6-v2')  # lightweight, fast, good for matching

def load_jobs(csv_path):
    df = pd.read_csv(csv_path)
    return df

def embed_descriptions(df):
    descriptions = df['description'].tolist()
    embeddings = model.encode(descriptions, show_progress_bar=True)
    return np.array(embeddings).astype("float32")

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def embed_resume(resume_path, model):
    text = extract_resume_text(resume_path)
    return model.encode([text])[0], text

def find_top_jobs(resume_vector, job_embeddings, index, top_k=3):
    distances, indices = index.search(np.array([resume_vector]).astype("float32"), top_k)
    return indices[0], distances[0]

def detect_missing_skills(resume_text, job_desc):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_desc))
    missing = job_skills - resume_skills
    return list(missing)