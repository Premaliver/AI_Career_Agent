from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SourceAccess(str, Enum):
    OFFICIAL_API = "official_api"
    PARTNER_API = "partner_api"
    PUBLIC_FEED = "public_feed"
    PUBLIC_PAGE = "public_page"
    UNSUPPORTED = "unsupported"


class WorkMode(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    ANY = "any"


@dataclass(slots=True)
class CandidateProfile:
    full_name: str = "Unknown"
    skills: list[str] = field(default_factory=list)
    years_experience: int = 0
    projects: list[str] = field(default_factory=list)
    education: str = "Not specified"
    certifications: list[str] = field(default_factory=list)
    preferred_roles: list[str] = field(default_factory=list)
    location: str = "Not specified"
    work_mode: WorkMode = WorkMode.ANY
    seniority_level: str = "entry"


@dataclass(slots=True)
class JobListing:
    source: str
    source_access: SourceAccess
    external_id: str
    title: str
    company: str
    location: str
    description: str
    apply_url: str
    skills: list[str] = field(default_factory=list)
    salary_min: int | None = None
    salary_max: int | None = None
    experience_min: int | None = None
    experience_max: int | None = None
    work_mode: WorkMode = WorkMode.ANY
    posted_at: datetime | None = None
    expires_at: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JobMatch:
    job: JobListing
    match_score: float
    missing_skills: list[str]
    explanation: str
    matched_skills: list[str]
    factors: dict[str, float]
