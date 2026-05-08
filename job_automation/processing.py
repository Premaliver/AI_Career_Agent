from __future__ import annotations

import re
from datetime import datetime, timezone

from .models import JobListing, JobMatch


def normalize_job(job: JobListing) -> JobListing:
    job.title = _clean(job.title)
    job.company = _clean(job.company)
    job.location = _clean(job.location)
    job.description = re.sub(r"<[^>]+>", " ", job.description or "")
    job.description = _clean(job.description)
    job.skills = sorted({skill.lower().strip() for skill in job.skills if skill.strip()})
    return job


def dedupe_jobs(jobs: list[JobListing]) -> list[JobListing]:
    seen: set[str] = set()
    result: list[JobListing] = []
    for job in jobs:
        key = "|".join(
            [
                job.company.lower(),
                job.title.lower(),
                job.location.lower(),
                re.sub(r"\?.*$", "", job.apply_url.lower()),
            ]
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(job)
    return result


def filter_quality(jobs: list[JobListing]) -> list[JobListing]:
    now = datetime.now(timezone.utc)
    filtered = []
    for job in jobs:
        if not job.apply_url or not job.title or not job.company:
            continue
        if job.expires_at and job.expires_at < now:
            continue
        if _looks_spammy(job):
            continue
        filtered.append(job)
    return filtered


def shortlist(matches: list[JobMatch], limit: int = 10) -> list[JobMatch]:
    return sorted(matches, key=lambda item: item.match_score, reverse=True)[:limit]


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _looks_spammy(job: JobListing) -> bool:
    text = f"{job.title} {job.company} {job.description}".lower()
    blocked = ["pay to apply", "registration fee", "earn from home daily", "whatsapp only"]
    return any(term in text for term in blocked)
