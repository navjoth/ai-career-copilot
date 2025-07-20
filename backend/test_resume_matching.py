from extractors.job_embedder import (
    load_jobs, embed_descriptions, build_faiss_index,
    embed_resume, find_top_jobs, detect_missing_skills, model
)

csv_path = "jobs/sample_jobs.csv"
resume_path = "data/resume_2.pdf" 

# Step 1: Load and embed jobs
df = load_jobs(csv_path)
job_embeddings = embed_descriptions(df)
index = build_faiss_index(job_embeddings)

# Step 2: Embed resume
resume_vector, resume_text = embed_resume(resume_path, model)

# Step 3: Find top 3 matching jobs
top_indices, distances = find_top_jobs(resume_vector, job_embeddings, index)

print("\n--- Top 3 Matching Jobs ---")
for i, idx in enumerate(top_indices):
    job = df.iloc[idx]
    print(f"\nRank {i+1}: {job['title']} at {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Similarity Score: {1 - distances[i]:.2f}")  # Lower distance = better match
    print(f"Description: {job['description']}")

    # Step 4: Detect missing skills
    missing = detect_missing_skills(resume_text, job['description'])
    print("Missing Skills:", missing if missing else "None 🎯")
