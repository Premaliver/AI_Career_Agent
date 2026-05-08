from __future__ import annotations

import logging
from dataclasses import asdict

from .models import CandidateProfile, JobMatch

logger = logging.getLogger(__name__)


class NotificationService:
    def send_in_app(self, user_id: str, matches: list[JobMatch]) -> None:
        # Replace this with a DB insert into job_recommendations/notifications.
        logger.info("Prepared %s in-app job recommendations for user %s", len(matches), user_id)

    def send_email_digest(self, email: str, matches: list[JobMatch]) -> None:
        # Wire to SMTP, SendGrid, SES, or Mailgun in production.
        logger.info("Prepared email digest for %s with %s jobs", email, len(matches))

    def send_instant_alerts(self, profile: CandidateProfile, matches: list[JobMatch]) -> None:
        logger.info("Instant alerts ready for %s: %s jobs", profile.full_name, len(matches))


def match_to_dict(match: JobMatch) -> dict:
    data = asdict(match)
    data["job"]["posted_at"] = match.job.posted_at.isoformat() if match.job.posted_at else None
    data["job"]["expires_at"] = match.job.expires_at.isoformat() if match.job.expires_at else None
    return data
