from __future__ import annotations

import re

from resume_parser import extract_education, extract_experience_years, extract_skills

from .models import CandidateProfile, WorkMode


ROLE_SKILL_MAP = {
    "Python Developer": {"python", "django", "flask", "fastapi", "sql", "rest api"},
    "Data Analyst": {"sql", "excel", "power bi", "tableau", "pandas", "data analysis"},
    "Frontend Developer": {"javascript", "typescript", "react", "html", "css", "next.js"},
    "Machine Learning Engineer": {"python", "machine learning", "deep learning", "pytorch", "tensorflow"},
    "Backend Developer": {"python", "java", "node.js", "django", "fastapi", "sql", "mongodb"},
}


def build_candidate_profile(
    resume_text: str,
    resume_skills: list[str] | None = None,
    preferred_role: str | None = None,
    location: str | None = None,
    work_mode: str | None = None,
) -> CandidateProfile:
    skills = resume_skills or extract_skills(resume_text)
    years = extract_experience_years(resume_text)
    education = extract_education(resume_text)

    roles = [preferred_role] if preferred_role else infer_roles(skills)
    return CandidateProfile(
        full_name=_extract_name(resume_text),
        skills=skills,
        years_experience=years,
        projects=_extract_projects(resume_text),
        education=education,
        certifications=_extract_certifications(resume_text),
        preferred_roles=roles,
        location=location or _extract_location(resume_text),
        work_mode=_parse_work_mode(work_mode or resume_text),
        seniority_level=_seniority(years),
    )


def infer_roles(skills: list[str]) -> list[str]:
    skill_set = {skill.lower() for skill in skills}
    scored = []
    for role, role_skills in ROLE_SKILL_MAP.items():
        overlap = len(skill_set & role_skills)
        if overlap:
            scored.append((overlap / len(role_skills), role))
    scored.sort(reverse=True)
    return [role for _, role in scored[:3]] or ["Software Developer"]


def normalize_skills(skills: list[str]) -> list[str]:
    return sorted({skill.strip().lower() for skill in skills if skill and skill.strip()})


def _extract_name(text: str) -> str:
    for line in text.splitlines()[:8]:
        candidate = line.strip()
        if 2 <= len(candidate.split()) <= 4 and not re.search(r"@|http|\d", candidate):
            return candidate
    return "Unknown"


def _extract_projects(text: str) -> list[str]:
    projects = []
    capture = False
    for line in text.splitlines():
        clean = line.strip(" -\t")
        if re.search(r"\b(projects?|portfolio)\b", clean, re.I):
            capture = True
            continue
        if capture and clean:
            if re.search(r"\b(education|experience|skills|certifications?)\b", clean, re.I):
                break
            projects.append(clean[:140])
        if len(projects) >= 5:
            break
    return projects


def _extract_certifications(text: str) -> list[str]:
    certs = []
    for line in text.splitlines():
        if re.search(r"\b(certification|certified|certificate|aws|azure|google cloud)\b", line, re.I):
            certs.append(line.strip()[:140])
    return certs[:5]


def _extract_location(text: str) -> str:
    patterns = [
        r"\b(?:location|address)\s*[:\-]\s*([A-Za-z ,.-]{2,80})",
        r"\b(Bengaluru|Bangalore|Hyderabad|Pune|Mumbai|Delhi|Gurugram|Noida|Chennai|Kolkata|Remote)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip()
    return "Not specified"


def _parse_work_mode(value: str) -> WorkMode:
    lowered = value.lower()
    if "remote" in lowered:
        return WorkMode.REMOTE
    if "hybrid" in lowered:
        return WorkMode.HYBRID
    if "onsite" in lowered or "on-site" in lowered:
        return WorkMode.ONSITE
    return WorkMode.ANY


def _seniority(years: int) -> str:
    if years >= 8:
        return "senior"
    if years >= 3:
        return "mid"
    if years >= 1:
        return "junior"
    return "entry"
