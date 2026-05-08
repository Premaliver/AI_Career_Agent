"""
matcher.py — AI Resume Screener
Matches resume skills against job description skills.
Returns match percentage, matched skills, missing skills, and a fit label.
"""
 
# ── Skill importance weights by category ──────────────────────────────────────
# Skills in this map get a higher weight (default weight = 1)
SKILL_WEIGHTS = {
    # Core programming — high weight
    "python": 1.5, "java": 1.5, "javascript": 1.5, "typescript": 1.3,
    "c++": 1.4, "c#": 1.4, "go": 1.3, "rust": 1.3,
 
    # AI/ML — highest weight (hot market)
    "machine learning": 2.0, "deep learning": 2.0, "nlp": 1.8,
    "computer vision": 1.8, "tensorflow": 1.5, "pytorch": 1.5,
    "data science": 1.8, "generative ai": 2.0,
 
    # Cloud & DevOps — high weight
    "aws": 1.5, "azure": 1.4, "gcp": 1.4, "docker": 1.4,
    "kubernetes": 1.5, "ci/cd": 1.3,
 
    # Databases — medium-high
    "sql": 1.3, "mongodb": 1.2,
 
    # Soft skills — lower weight
    "communication": 0.7, "leadership": 0.8, "agile": 0.9,
}
 
 
def get_weight(skill: str) -> float:
    return SKILL_WEIGHTS.get(skill.lower(), 1.0)
 
 
def match_skills(resume_skills: list, job_skills: list) -> dict:
    """
    Compare resume skills to job skills.
 
    Returns a dict with:
      - match_percent     : weighted match percentage (0–100)
      - raw_match_percent : simple count-based match percentage
      - matched           : list of skills present in both
      - missing           : list of skills in job but not in resume
      - extra             : list of skills in resume but not in job (bonus)
      - fit_level         : "Excellent" | "Good" | "Moderate" | "Needs Work" | "Low"
      - fit_emoji         : emoji for fit level
      - verdict           : one-line summary string
    """
    if not job_skills:
        return _empty_result()
 
    resume_set = set(s.lower() for s in resume_skills)
    job_set    = set(s.lower() for s in job_skills)
 
    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)
    extra   = sorted(resume_set - job_set)
 
    # Weighted scoring
    total_weight   = sum(get_weight(s) for s in job_set)
    matched_weight = sum(get_weight(s) for s in matched)
 
    match_percent     = round((matched_weight / total_weight) * 100, 1) if total_weight else 0
    raw_match_percent = round((len(matched) / len(job_set)) * 100, 1)
 
    fit_level, fit_emoji = _get_fit(match_percent)
    verdict = _get_verdict(fit_level, match_percent, len(missing))
 
    return {
        "match_percent":     match_percent,
        "raw_match_percent": raw_match_percent,
        "matched":           matched,
        "missing":           missing,
        "extra":             extra,
        "fit_level":         fit_level,
        "fit_emoji":         fit_emoji,
        "verdict":           verdict,
        "total_job_skills":  len(job_set),
        "total_matched":     len(matched),
        "total_missing":     len(missing),
    }
 
 
def _get_fit(percent: float):
    if percent >= 80:
        return "Excellent", "🟢"
    elif percent >= 60:
        return "Good", "🔵"
    elif percent >= 40:
        return "Moderate", "🟡"
    elif percent >= 20:
        return "Needs Work", "🟠"
    else:
        return "Low", "🔴"
 
 
def _get_verdict(fit_level: str, percent: float, missing_count: int) -> str:
    verdicts = {
        "Excellent": f"Strong match ({percent}%)! You're highly qualified — apply with confidence.",
        "Good":      f"Good match ({percent}%). A few skill gaps; sharpen them to stand out.",
        "Moderate":  f"Moderate match ({percent}%). Bridge {missing_count} skill(s) to be competitive.",
        "Needs Work": f"Partial match ({percent}%). Significant gaps — build {missing_count} key skill(s) first.",
        "Low":       f"Low match ({percent}%). This role needs major upskilling before applying.",
    }
    return verdicts.get(fit_level, f"Match: {percent}%")
 
 
def _empty_result() -> dict:
    return {
        "match_percent": 0,
        "raw_match_percent": 0,
        "matched": [],
        "missing": [],
        "extra": [],
        "fit_level": "Unknown",
        "fit_emoji": "⚪",
        "verdict": "No job skills detected. Please provide a detailed job description.",
        "total_job_skills": 0,
        "total_matched": 0,
        "total_missing": 0,
    }