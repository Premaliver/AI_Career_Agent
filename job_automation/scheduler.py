"""Background refresh entry points.

Production deployment should call these from Celery Beat, APScheduler, or a
managed queue. This module stays dependency-light so the current Flask app is
not forced to install Redis/Celery during development.
"""

from __future__ import annotations

from .pipeline import run_job_automation


def refresh_matches_for_resume(
    resume_text: str,
    resume_skills: list[str],
    user_id: str,
    email: str | None = None,
) -> dict:
    return run_job_automation(
        resume_text=resume_text,
        resume_skills=resume_skills,
        user_id=user_id,
        email=email,
    )
