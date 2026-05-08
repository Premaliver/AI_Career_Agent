from __future__ import annotations

import logging
import os

from .connectors import DemoConnector, GreenhouseConnector, JobSourceConnector, LeverConnector
from .matching import score_job
from .models import CandidateProfile, JobMatch
from .notifications import NotificationService, match_to_dict
from .processing import dedupe_jobs, filter_quality, normalize_job, shortlist
from .profile import build_candidate_profile

logger = logging.getLogger(__name__)


def build_default_connectors() -> list[JobSourceConnector]:
    connectors: list[JobSourceConnector] = []

    greenhouse_tokens = _csv_env("GREENHOUSE_BOARD_TOKENS")
    lever_sites = _csv_env("LEVER_SITE_NAMES")
    if greenhouse_tokens:
        connectors.append(GreenhouseConnector(greenhouse_tokens))
    if lever_sites:
        connectors.append(LeverConnector(lever_sites))

    if os.environ.get("JOB_AUTOMATION_DEMO", "true").lower() == "true":
        connectors.append(DemoConnector())
    return connectors


def run_job_automation(
    resume_text: str,
    resume_skills: list[str],
    user_id: str = "anonymous",
    email: str | None = None,
    preferred_role: str | None = None,
    location: str | None = None,
    work_mode: str | None = None,
    connectors: list[JobSourceConnector] | None = None,
    limit: int = 10,
) -> dict:
    profile = build_candidate_profile(
        resume_text=resume_text,
        resume_skills=resume_skills,
        preferred_role=preferred_role,
        location=location,
        work_mode=work_mode,
    )
    active_connectors = connectors if connectors is not None else build_default_connectors()

    raw_jobs = []
    errors = []
    for connector in active_connectors:
        try:
            raw_jobs.extend(connector.fetch(profile, limit=25))
        except Exception as exc:
            logger.warning("Job connector failed: %s: %s", connector.name, exc)
            errors.append({"source": connector.name, "error": str(exc)})

    normalized = [normalize_job(job) for job in raw_jobs]
    clean_jobs = filter_quality(dedupe_jobs(normalized))
    matches: list[JobMatch] = shortlist([score_job(profile, job) for job in clean_jobs], limit=limit)

    notifications = NotificationService()
    notifications.send_in_app(user_id, matches)
    if email:
        notifications.send_email_digest(email, matches)

    return {
        "profile": profile,
        "matches": matches,
        "matches_json": [match_to_dict(match) for match in matches],
        "connector_errors": errors,
        "sources_used": [connector.name for connector in active_connectors],
    }


def _csv_env(name: str) -> list[str]:
    value = os.environ.get(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]
