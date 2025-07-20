import spacy

nlp = spacy.load("en_core_web_sm")

# Predefined tech + common job skills
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "aws", "azure", "gcp", "linux",
    "docker", "kubernetes", "tensorflow", "pytorch", "spark", "hadoop",
    "pandas", "numpy", "scikit-learn", "ml", "nlp", "git", "rest", "api",
    "flask", "django", "react", "node.js", "agile", "jira", "ci/cd", "terraform",
    "data analysis", "data engineering", "machine learning", "deep learning"
]


def extract_skills(text):
    doc = nlp(text.lower())
    tokens = set([token.text for token in doc if not token.is_stop])

    # Match common skills
    found = set()
    for skill in COMMON_SKILLS:
        if skill in tokens or skill in text.lower():
            found.add(skill)

    return list(found)

def extract_education(text):
    education_section = ""
    match = re.search(r"(education|educational background)(.*?)(experience|projects|skills|$)", text, re.DOTALL | re.IGNORECASE)
    if match:
        education_section = match.group(2).strip()
    return education_section

def extract_experience(text):
    lines = text.split('\n')

    # Normalize section headers
    section_headers = [line.strip().lower() for line in lines]

    # Known headers to trigger experience capture
    experience_headers = [
        "experience",
        "work experience",
        "professional experience",
        "internship experience"
    ]

    # Known headers to stop capture
    stop_headers = [
        "education", "skills", "projects", "certifications", "achievements", "languages"
    ]

    capturing = False
    experience_lines = []

    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

        if not capturing and line_lower in experience_headers:
            capturing = True
            continue

        # If we hit another section, stop capturing
        if capturing and (line_lower in stop_headers or line_stripped.isupper()):
            break

        if capturing:
            experience_lines.append(line_stripped)

    return "\n".join(experience_lines).strip()
