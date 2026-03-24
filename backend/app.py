# ==========================================
# FLASK BACKEND — Resume Analyzer API
# ==========================================

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import from utils
from utils import (
    extract_text_from_pdf,
    preprocess_text,
    extract_skills,
    get_all_skills,
    calculate_similarity,
    calculate_skill_match,
    get_missing_skills,
    map_resume_skills,
    generate_suggestions,
    recommend_jobs_domain_based
)

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "Resume Analyzer API is running 🚀"


# ==========================================
# MAIN API ROUTE
# ==========================================
@app.route("/analyze", methods=["POST"])
def analyze():

    try:
        # ================================
        # 1. GET INPUTS
        # ================================
        file = request.files.get("resume")
        jd = request.form.get("jd")

        if not file or not jd:
            return jsonify({"error": "Resume or Job Description missing"}), 400

        # ================================
        # 2. EXTRACT TEXT
        # ================================
        raw_text = extract_text_from_pdf(file)

        if len(raw_text.strip()) < 50:
            return jsonify({"error": "Resume not readable (ATS issue)"}), 400

        # ================================
        # 3. PREPROCESS
        # ================================
        clean_text = preprocess_text(raw_text)
        jd_clean = preprocess_text(jd)

        # ================================
        # 4. SKILL EXTRACTION
        # ================================
        resume_skill_dict = extract_skills(clean_text)
        jd_skill_dict = extract_skills(jd_clean)

        resume_skills = get_all_skills(resume_skill_dict)
        jd_skills = get_all_skills(jd_skill_dict)

        # ================================
        # 5. MAP SKILLS (SQL FIX etc.)
        # ================================
        resume_skills_mapped = map_resume_skills(resume_skills)

        # ================================
        # 6. SCORING
        # ================================
        skill_score = calculate_skill_match(resume_skills_mapped, jd_skills)

        resume_text_for_match = clean_text
        jd_text_for_match = " ".join(jd_skills)

        tfidf_score = calculate_similarity(resume_text_for_match, jd_text_for_match)

        final_score = round((0.7 * skill_score) + (0.3 * tfidf_score), 2)

        # ================================
        # 7. MISSING SKILLS
        # ================================
        missing_skills = get_missing_skills(resume_skills_mapped, jd_skills)

        # ================================
        # 8. SUGGESTIONS + JOBS
        # ================================
        suggestions = generate_suggestions(final_score, missing_skills)
        jobs, domain = recommend_jobs_domain_based(resume_skills_mapped)

        # ================================
        # 9. RESPONSE
        # ================================
        return jsonify({
            "score": final_score,
            "skill_score": skill_score,
            "tfidf_score": tfidf_score,
            "domain": domain,
            "resume_skills": resume_skills_mapped,
            "jd_skills": jd_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "jobs": jobs,
            "skills": resume_skills_mapped
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# RUN SERVER
# ==========================================
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)