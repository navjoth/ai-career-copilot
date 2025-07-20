from extractors.job_embedder import load_jobs, embed_descriptions, build_faiss_index

csv_path = "jobs/sample_jobs.csv"
df = load_jobs(csv_path)
print(f"Loaded {len(df)} jobs")

embeddings = embed_descriptions(df)
print("Generated embeddings:", embeddings.shape)

index = build_faiss_index(embeddings)
print("FAISS index ready with", index.ntotal, "entries")
