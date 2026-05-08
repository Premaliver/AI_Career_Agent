"""Resume-to-Jobs Automation Engine.

This package is intentionally additive: it can be called after the existing
resume analysis pipeline without changing the current parser, matcher, or
roadmap behavior.
"""

from .pipeline import run_job_automation

__all__ = ["run_job_automation"]
