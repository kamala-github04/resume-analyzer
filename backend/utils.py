# ==========================================
# UTILS FILE — Resume Analyzer Core Logic
# ==========================================

import re
import pdfplumber
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download stopwords (first time only)
nltk.download('stopwords')


# ==========================================
# 1. EXTRACT TEXT FROM PDF
# ==========================================
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text


# ==========================================
# 2. NORMALIZATION
# ==========================================
def normalize_text(text):
    replacements = {
        r"\bml\b": "machine learning",
        r"\bai\b": "artificial intelligence",
        r"\bjs\b": "javascript"
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    return text


# ==========================================
# 3. PREPROCESS TEXT
# ==========================================
def preprocess_text(text):
    text = text.lower()

    text = re.sub(r'cid:\d+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    text = normalize_text(text)

    text = re.sub(r'\s+', ' ', text).strip()

    words = text.split()

    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    return " ".join(words)


# ==========================================
# 4. SKILL DATABASE
# ==========================================
skills_db = {
    "programming": ["python","java","c++","c","javascript"],
    "web": ["html","css","react","node","angular","mern"],
    "database": ["sql","mongodb","mysql","oracle","postgresql"],
    "data_science": [
        "machine learning","deep learning",
        "pandas","numpy","tensorflow","keras",
        "scikit-learn","matplotlib"
    ],
    "tools": [
        "git","docker","kubernetes","jupyter",
        "blender","linux","pygame","pytest"
    ],
    "cloud": ["aws","azure","gcp"],
    "soft_skills": ["communication","leadership","teamwork","team collaboration"],
    "core": ["mechanical","civil","electronics","accounting","marketing"]
}


# ==========================================
# 5. SKILL EXTRACTION
# ==========================================
def extract_skills(text):
    found_skills = {}

    text_words = set(text.split())

    for category, skills in skills_db.items():
        found = []

        for skill in skills:
            if skill in text_words:
                found.append(skill)
            elif re.search(r'\b' + re.escape(skill) + r'\b', text):
                found.append(skill)

        if found:
            found_skills[category] = list(set(found))

    # Handle MERN
    if "mern" in text:
        if "web" not in found_skills:
            found_skills["web"] = []

        found_skills["web"].extend(["mongodb", "react", "node"])
        found_skills["web"] = list(set(found_skills["web"]))

    return found_skills


# ==========================================
# 6. FLATTEN SKILLS
# ==========================================
def get_all_skills(skill_dict):
    all_skills = []
    for skills in skill_dict.values():
        all_skills.extend(skills)
    return list(set(all_skills))


# ==========================================
# 7. TF-IDF SIMILARITY
# ==========================================
def calculate_similarity(resume_text, jd_text):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(score * 100, 2)


# ==========================================
# 8. SKILL MATCH SCORE
# ==========================================
def calculate_skill_match(resume_skills, jd_skills):
    matched = set(resume_skills) & set(jd_skills)

    if len(jd_skills) == 0:
        return 0

    score = (len(matched) / len(jd_skills)) * 100
    return round(score, 2)


# ==========================================
# 9. MISSING SKILLS
# ==========================================
def get_missing_skills(resume_skills, jd_skills):
    return list(set(jd_skills) - set(resume_skills))


# ==========================================
# 10. SKILL EQUIVALENCE
# ==========================================
skill_equivalence = {
    "mysql": "sql",
    "oracle": "sql",
    "postgresql": "sql"
}

skill_synonyms = {
    "team collaboration": "teamwork",
    "working in team": "teamwork",
    "collaborated": "teamwork"
}


def map_resume_skills(skills):
    mapped = []

    for s in skills:
        s = skill_equivalence.get(s, s)
        s = skill_synonyms.get(s, s)
        mapped.append(s)

    return list(set(mapped))


# ==========================================
# 11. SUGGESTIONS
# ==========================================
def generate_suggestions(score, missing_skills):
    suggestions = []

    if score < 60:
        suggestions.append("Improve your resume to better match the job description")
        suggestions.append("Add more relevant projects")

    if missing_skills:
        suggestions.append(f"Learn and include these skills: {', '.join(missing_skills)}")

    if "machine learning" in missing_skills:
        suggestions.append("Add ML projects like prediction systems or NLP-based apps")

    suggestions.append("Use strong action verbs like 'developed', 'implemented'")
    suggestions.append("Add measurable achievements (e.g., improved performance by 30%)")
    suggestions.append("Keep resume ATS-friendly (avoid tables, images)")

    return suggestions


# ==========================================
# 12. DOMAIN DETECTION
# ==========================================
def detect_domain(skills):
    domains = {
        "tech": ["python", "java", "react", "node", "sql"],
        "data": ["pandas", "numpy", "machine learning", "tensorflow"],
        "web": ["html", "css", "react"],
        "hr": ["recruitment", "communication", "hr"],
        "marketing": ["digital marketing", "content writing"],
        "business": ["excel", "analysis", "power bi"]
    }

    scores = {}
    for domain, keywords in domains.items():
        scores[domain] = len(set(skills) & set(keywords))

    best_domain = max(scores, key=scores.get)

    if scores[best_domain] == 0:
        return "unknown"

    return best_domain


# ==========================================
# 13. JOB RECOMMENDATION
# ==========================================
def recommend_jobs_domain_based(skills):
    domain = detect_domain(skills)
    jobs = {}

    if domain == "tech":
        if "java" in skills:
            jobs["Software Developer"] = 85
        if "node" in skills:
            jobs["Backend Developer"] = 88

    elif domain == "data":
        jobs["Data Analyst"] = 90
        if "machine learning" in skills:
            jobs["Machine Learning Engineer"] = 85

    elif domain == "web":
        jobs["Frontend Developer"] = 88
        jobs["Full Stack Developer"] = 90

    elif domain == "hr":
        jobs["HR Executive"] = 90

    elif domain == "marketing":
        jobs["Marketing Executive"] = 85
        jobs["Digital Marketing Specialist"] = 88

    elif domain == "business":
        jobs["Business Analyst"] = 90

    else:
        jobs["General Role"] = 70

    return sorted(jobs.items(), key=lambda x: x[1], reverse=True), domain