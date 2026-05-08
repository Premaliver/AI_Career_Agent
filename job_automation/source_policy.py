from __future__ import annotations

from dataclasses import dataclass

from .models import SourceAccess


@dataclass(frozen=True, slots=True)
class SourcePolicy:
    name: str
    access: SourceAccess
    enabled_by_default: bool
    notes: str
    requires_approval: bool = False


SOURCE_POLICIES: dict[str, SourcePolicy] = {
    "greenhouse": SourcePolicy(
        name="greenhouse",
        access=SourceAccess.OFFICIAL_API,
        enabled_by_default=True,
        notes="Use Greenhouse Job Board API for public board tokens.",
    ),
    "lever": SourcePolicy(
        name="lever",
        access=SourceAccess.OFFICIAL_API,
        enabled_by_default=True,
        notes="Use Lever Postings API for known company site names.",
    ),
    "google_jobposting_feed": SourcePolicy(
        name="google_jobposting_feed",
        access=SourceAccess.PUBLIC_FEED,
        enabled_by_default=False,
        notes="Use employer-owned sitemaps/RSS/Atom pages with JobPosting markup only when allowed.",
        requires_approval=True,
    ),
    "microsoft_careers": SourcePolicy(
        name="microsoft_careers",
        access=SourceAccess.PUBLIC_PAGE,
        enabled_by_default=False,
        notes="Use only if Microsoft provides an approved API/feed or explicit crawl permission.",
        requires_approval=True,
    ),
    "linkedin": SourcePolicy(
        name="linkedin",
        access=SourceAccess.PARTNER_API,
        enabled_by_default=False,
        notes="Partner/Talent Solutions APIs only. Do not scrape LinkedIn pages.",
        requires_approval=True,
    ),
    "indeed": SourcePolicy(
        name="indeed",
        access=SourceAccess.PARTNER_API,
        enabled_by_default=False,
        notes="Indeed APIs are partner/OAuth governed. Do not scrape search result pages.",
        requires_approval=True,
    ),
    "naukri": SourcePolicy(
        name="naukri",
        access=SourceAccess.UNSUPPORTED,
        enabled_by_default=False,
        notes="Treat as unsupported unless you obtain a documented API/feed agreement.",
        requires_approval=True,
    ),
    "internshala": SourcePolicy(
        name="internshala",
        access=SourceAccess.UNSUPPORTED,
        enabled_by_default=False,
        notes="Treat as unsupported unless explicit automation permission exists.",
        requires_approval=True,
    ),
}


def is_source_allowed(source_name: str) -> bool:
    policy = SOURCE_POLICIES.get(source_name)
    if not policy:
        return False
    return policy.enabled_by_default and policy.access != SourceAccess.UNSUPPORTED
