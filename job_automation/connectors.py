from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Iterable

import requests

from resume_parser import extract_skills

from .models import CandidateProfile, JobListing, SourceAccess, WorkMode
from .source_policy import is_source_allowed


class JobSourceConnector(ABC):
    name: str
    access: SourceAccess

    @abstractmethod
    def fetch(self, profile: CandidateProfile, limit: int = 20) -> list[JobListing]:
        raise NotImplementedError


class GreenhouseConnector(JobSourceConnector):
    name = "greenhouse"
    access = SourceAccess.OFFICIAL_API

    def __init__(self, board_tokens: Iterable[str], timeout: int = 10):
        self.board_tokens = list(board_tokens)
        self.timeout = timeout

    def fetch(self, profile: CandidateProfile, limit: int = 20) -> list[JobListing]:
        if not is_source_allowed(self.name):
            return []

        jobs: list[JobListing] = []
        for token in self.board_tokens:
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
            response = requests.get(url, params={"content": "true"}, timeout=self.timeout)
            response.raise_for_status()
            for item in response.json().get("jobs", []):
                description = item.get("content") or ""
                jobs.append(
                    JobListing(
                        source=self.name,
                        source_access=self.access,
                        external_id=f"{token}:{item.get('id')}",
                        title=item.get("title") or "Untitled",
                        company=token,
                        location=(item.get("location") or {}).get("name") or "Not specified",
                        description=description,
                        apply_url=item.get("absolute_url") or "",
                        skills=extract_skills(description),
                        posted_at=_parse_dt(item.get("updated_at")),
                        raw=item,
                    )
                )
                if len(jobs) >= limit:
                    return jobs
        return jobs


class LeverConnector(JobSourceConnector):
    name = "lever"
    access = SourceAccess.OFFICIAL_API

    def __init__(self, site_names: Iterable[str], timeout: int = 10):
        self.site_names = list(site_names)
        self.timeout = timeout

    def fetch(self, profile: CandidateProfile, limit: int = 20) -> list[JobListing]:
        if not is_source_allowed(self.name):
            return []

        jobs: list[JobListing] = []
        for site in self.site_names:
            url = f"https://api.lever.co/v0/postings/{site}"
            response = requests.get(url, params={"mode": "json"}, timeout=self.timeout)
            response.raise_for_status()
            for item in response.json():
                description = " ".join(
                    str(item.get(key) or "") for key in ("descriptionPlain", "additionalPlain")
                )
                categories = item.get("categories") or {}
                jobs.append(
                    JobListing(
                        source=self.name,
                        source_access=self.access,
                        external_id=f"{site}:{item.get('id')}",
                        title=item.get("text") or "Untitled",
                        company=site,
                        location=categories.get("location") or "Not specified",
                        description=description,
                        apply_url=item.get("hostedUrl") or "",
                        skills=extract_skills(description),
                        work_mode=_work_mode_from_text(" ".join([description, categories.get("commitment", "")])),
                        posted_at=_parse_timestamp_ms(item.get("createdAt")),
                        raw=item,
                    )
                )
                if len(jobs) >= limit:
                    return jobs
        return jobs


class DemoConnector(JobSourceConnector):
    """Local connector for development when no external API credentials are set."""

    name = "demo"
    access = SourceAccess.PUBLIC_FEED

    def fetch(self, profile: CandidateProfile, limit: int = 20) -> list[JobListing]:
        role = profile.preferred_roles[0] if profile.preferred_roles else "Software Developer"
        base_skills = profile.skills[:5] or ["python", "sql", "git"]
        return [
            JobListing(
                source=self.name,
                source_access=self.access,
                external_id=f"demo-{index}",
                title=title,
                company=company,
                location=profile.location if profile.location != "Not specified" else "Remote",
                description=f"{title} role using {', '.join(base_skills)} with REST APIs and agile delivery.",
                apply_url="https://example.com/apply",
                skills=base_skills + ["rest api", "agile"],
                work_mode=profile.work_mode,
                posted_at=datetime.now(timezone.utc),
            )
            for index, (title, company) in enumerate(
                [
                    (role, "DemoTech Labs"),
                    (f"Junior {role}", "CareerCloud"),
                    (f"{role} Intern", "SkillBridge"),
                ],
                start=1,
            )
        ][:limit]


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_timestamp_ms(value: int | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


def _work_mode_from_text(text: str) -> WorkMode:
    lowered = text.lower()
    if "remote" in lowered:
        return WorkMode.REMOTE
    if "hybrid" in lowered:
        return WorkMode.HYBRID
    if "onsite" in lowered or "on-site" in lowered:
        return WorkMode.ONSITE
    return WorkMode.ANY
