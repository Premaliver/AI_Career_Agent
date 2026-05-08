from __future__ import annotations

from datetime import datetime, timezone

from matcher import match_skills

from .models import CandidateProfile, JobListing, JobMatch, WorkMode


def score_job(profile: CandidateProfile, job: JobListing) -> JobMatch:
    skill_match = match_skills(profile.skills, job.skills)
    skill_score = float(skill_match.get("match_percent", 0))
    exp_score = _experience_fit(profile.years_experience, job)
    location_score = _location_fit(profile, job)
    remote_score = _remote_fit(profile.work_mode, job.work_mode)
    recency_score = _recency(job)
    company_score = 65.0

    factors = {
        "skill_match": skill_score,
        "experience_fit": exp_score,
        "location_fit": location_score,
        "remote_fit": remote_score,
        "recency": recency_score,
        "company_relevance": company_score,
    }
    total = (
        skill_score * 0.42
        + exp_score * 0.18
        + location_score * 0.14
        + remote_score * 0.10
        + recency_score * 0.10
        + company_score * 0.06
    )

    matched = skill_match.get("matched", [])
    missing = skill_match.get("missing", [])
    explanation = _explain(job, matched, missing, profile)
    return JobMatch(
        job=job,
        match_score=round(total, 1),
        missing_skills=missing,
        explanation=explanation,
        matched_skills=matched,
        factors={key: round(value, 1) for key, value in factors.items()},
    )


def _experience_fit(years: int, job: JobListing) -> float:
    if job.experience_min is None and job.experience_max is None:
        return 75.0
    minimum = job.experience_min or 0
    maximum = job.experience_max or max(minimum + 4, 12)
    if minimum <= years <= maximum:
        return 100.0
    if years < minimum:
        return max(20.0, 100.0 - ((minimum - years) * 22.0))
    return max(60.0, 100.0 - ((years - maximum) * 8.0))


def _location_fit(profile: CandidateProfile, job: JobListing) -> float:
    if job.work_mode == WorkMode.REMOTE or profile.work_mode == WorkMode.REMOTE:
        return 95.0
    if profile.location == "Not specified" or job.location == "Not specified":
        return 70.0
    return 100.0 if profile.location.lower() in job.location.lower() else 45.0


def _remote_fit(preferred: WorkMode, actual: WorkMode) -> float:
    if preferred == WorkMode.ANY or actual == WorkMode.ANY:
        return 75.0
    if preferred == actual:
        return 100.0
    if preferred == WorkMode.REMOTE and actual == WorkMode.HYBRID:
        return 65.0
    return 45.0


def _recency(job: JobListing) -> float:
    if not job.posted_at:
        return 65.0
    age_days = max(0, (datetime.now(timezone.utc) - job.posted_at).days)
    if age_days <= 3:
        return 100.0
    if age_days <= 14:
        return 85.0
    if age_days <= 30:
        return 65.0
    return 35.0


def _explain(job: JobListing, matched: list[str], missing: list[str], profile: CandidateProfile) -> str:
    role_reason = f"The title aligns with {', '.join(profile.preferred_roles[:2]) or 'your inferred roles'}."
    skill_reason = (
        f"It matches your skills: {', '.join(matched[:5])}."
        if matched
        else "It is related to your target role but needs skill validation."
    )
    gap_reason = f"Main gaps: {', '.join(missing[:4])}." if missing else "No major skill gap found."
    return f"{role_reason} {skill_reason} {gap_reason}"
