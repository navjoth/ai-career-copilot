from extractors.resume_parser import extract_resume_text
from extractors.nlp_parser import extract_skills, extract_education, extract_experience

resume_path = "data/resume_2.pdf"  # ← Use your actual path here
text = extract_resume_text(resume_path)

print("\n--- Extracted Skills ---")
print(extract_skills(text))

print("\n--- Extracted Education ---")
print(extract_education(text))

print("\n--- Extracted Experience ---")
print(extract_experience(text))
