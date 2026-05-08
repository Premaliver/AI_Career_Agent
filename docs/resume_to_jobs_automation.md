# Resume-to-Jobs Automation Engine

This plan adds a job automation layer on top of the current Flask resume analyzer. The existing upload, parsing, skill gap, AI advice, and roadmap flow stays intact.

## Feature Plan

1. Candidate profile generation
   - Build a structured profile after PDF parsing: name, skills, years of experience, projects, education, certifications, inferred roles, location, work mode, seniority.
   - Current starter: `job_automation/profile.py`.
   - Production upgrade: store the profile and resume text hash in DB, then enrich with LLM extraction for projects/certifications/location.

2. Job discovery
   - Official API connectors first: Greenhouse Job Board API, Lever Postings API.
   - Partner-only connectors behind explicit credentials: LinkedIn Talent Solutions APIs, Indeed APIs, ZipRecruiter Partner Platform.
   - Public feed connectors only where permitted: employer-owned RSS/Atom/sitemap pages with JobPosting schema.
   - Unsupported by default: portals without official API/feed permission or clear automation terms.

3. Matching and ranking
   - Normalize skills with the existing `resume_parser.SKILLS_DB`.
   - Infer roles from profile skills.
   - Score by skill match, experience fit, location fit, salary fit, recency, company relevance, and work mode.
   - Return explanation, matched skills, missing skills, and ranking factors.

4. Notifications
   - Phase 1: in-app recommendations on result/dashboard.
   - Phase 2: email digest through SendGrid/SES/Mailgun.
   - Phase 3: WhatsApp Business API or Telegram Bot API for opt-in alerts.

5. Refresh automation
   - Use Celery Beat to refresh active alerts every 6-24 hours.
   - Store seen jobs per user to avoid duplicate notifications.
   - Notify only when score crosses the user's threshold or a newly posted job appears.

## Architecture

Recommended production services:

- Flask/FastAPI API service: upload, dashboard, user actions, alert preferences.
- Resume parser service: PDF extraction and structured profile creation.
- Profile enrichment service: LLM/NLP cleanup, role inference, skill taxonomy.
- Source connectors service: API/feed connector execution with source policy checks.
- Job normalization service: field cleaning, canonical URLs, dedupe, stale/spam filtering.
- AI ranking service: weighted matching plus optional embeddings.
- Notification service: in-app, email, WhatsApp/Telegram.
- Scheduler service: Celery workers and Celery Beat.
- Audit/logging service: connector attempts, policy decisions, user notifications, failures.

Current starter modules:

- `job_automation/models.py`: typed profile, job, source, match models.
- `job_automation/source_policy.py`: allowed/partner/unsupported policy layer.
- `job_automation/connectors.py`: Greenhouse, Lever, and demo connectors.
- `job_automation/processing.py`: normalization, dedupe, quality filtering.
- `job_automation/matching.py`: explainable scoring.
- `job_automation/notifications.py`: notification adapter stubs.
- `job_automation/pipeline.py`: orchestration.
- `job_automation/scheduler.py`: background refresh entry point.

## Database Schema

Use PostgreSQL for transactional data and pgvector later for embeddings.

```sql
create table users (
  id uuid primary key,
  email text unique,
  full_name text,
  created_at timestamptz default now()
);

create table resumes (
  id uuid primary key,
  user_id uuid references users(id),
  file_name text,
  text_hash text not null,
  parsed_text text,
  created_at timestamptz default now()
);

create table candidate_profiles (
  id uuid primary key,
  user_id uuid references users(id),
  resume_id uuid references resumes(id),
  full_name text,
  skills jsonb not null default '[]',
  years_experience int default 0,
  projects jsonb not null default '[]',
  education text,
  certifications jsonb not null default '[]',
  preferred_roles jsonb not null default '[]',
  location text,
  work_mode text,
  seniority_level text,
  created_at timestamptz default now()
);

create table source_policies (
  source text primary key,
  access_type text not null,
  enabled boolean not null default false,
  requires_approval boolean not null default true,
  notes text
);

create table job_listings (
  id uuid primary key,
  source text not null,
  source_access text not null,
  external_id text not null,
  title text not null,
  company text not null,
  location text,
  salary_min int,
  salary_max int,
  experience_min int,
  experience_max int,
  work_mode text,
  description text,
  skills jsonb not null default '[]',
  apply_url text not null,
  posted_at timestamptz,
  expires_at timestamptz,
  raw jsonb,
  created_at timestamptz default now(),
  unique (source, external_id)
);

create table job_matches (
  id uuid primary key,
  user_id uuid references users(id),
  job_id uuid references job_listings(id),
  match_score numeric(5,2),
  matched_skills jsonb not null default '[]',
  missing_skills jsonb not null default '[]',
  explanation text,
  factors jsonb not null default '{}',
  status text not null default 'recommended',
  created_at timestamptz default now(),
  unique (user_id, job_id)
);

create table job_alerts (
  id uuid primary key,
  user_id uuid references users(id),
  cadence text not null default 'daily',
  min_score numeric(5,2) default 70,
  channels jsonb not null default '["in_app"]',
  filters jsonb not null default '{}',
  active boolean not null default true,
  last_run_at timestamptz
);

create table notifications (
  id uuid primary key,
  user_id uuid references users(id),
  channel text not null,
  payload jsonb not null,
  status text not null default 'queued',
  sent_at timestamptz,
  created_at timestamptz default now()
);

create table audit_logs (
  id bigserial primary key,
  user_id uuid,
  event_type text not null,
  source text,
  metadata jsonb not null default '{}',
  created_at timestamptz default now()
);
```

## API Endpoint Design

Keep existing `/upload`. Add these endpoints when user accounts and persistence are introduced:

- `POST /api/resumes`: upload resume; returns `resume_id`, `profile_id`, current analysis, and queued job-search status.
- `GET /api/profiles/{profile_id}`: candidate profile.
- `POST /api/job-search/run`: manual refresh for a profile.
- `GET /api/jobs/recommended`: ranked job recommendations with filters.
- `POST /api/jobs/{match_id}/save`: save job.
- `POST /api/jobs/{match_id}/applied`: mark applied.
- `POST /api/jobs/{match_id}/hide`: reject/hide.
- `GET /api/job-alerts`: list alert settings.
- `POST /api/job-alerts`: create saved alert.
- `PATCH /api/job-alerts/{id}`: update cadence/channels/filters.
- `GET /api/audit/source-runs`: admin connector status and compliance trail.

## Connector Design

Each connector implements:

```python
class JobSourceConnector:
    name: str
    access: SourceAccess

    def fetch(self, profile: CandidateProfile, limit: int = 20) -> list[JobListing]:
        ...
```

Connector rules:

- Check `source_policy` before requests.
- Use official API/feed URLs.
- Respect rate limits and backoff.
- Store raw response for audit/debugging.
- Normalize into `JobListing`.
- Never scrape unsupported job search pages.

Environment examples:

```bash
GREENHOUSE_BOARD_TOKENS=airbnb,stripe
LEVER_SITE_NAMES=netflix,scaleai
JOB_AUTOMATION_DEMO=true
```

## Matching Logic

Initial score:

- skill match: 42%
- experience fit: 18%
- location fit: 14%
- remote/work mode fit: 10%
- recency: 10%
- company relevance: 6%

Production upgrades:

- Add salary fit when salary exists.
- Use embeddings for resume/project/job-description semantic similarity.
- Add negative signals for stale listings, vague descriptions, spam, and missing apply URL.
- Train weights from user feedback: saved, applied, hidden, ignored.

## Automation Workflow

1. User uploads resume.
2. Existing parser extracts text, skills, experience, education.
3. Existing analyzer creates skill gap report and roadmap.
4. Automation engine builds candidate profile.
5. Role inference creates search targets.
6. Connectors fetch jobs from allowed sources.
7. Pipeline normalizes, dedupes, filters, ranks.
8. Matches are saved and shown in dashboard.
9. Notifications are queued according to alert preferences.
10. Scheduler refreshes active profiles and alerts.

## Notification Workflow

- Instant alert: send top new jobs above threshold after upload or refresh.
- Daily digest: group new recommendations by score/source.
- Saved alerts: user-defined role, location, source, salary, experience, and work-mode filters.
- In-app tracker states: `recommended`, `saved`, `applied`, `hidden`, `expired`.

## Compliance Strategy

Source categories:

- Official APIs: enable by default when public/authorized, e.g. Greenhouse Job Board API and Lever Postings API.
- Partner-only APIs: disable by default; require written agreement/API credentials, e.g. LinkedIn Talent Solutions APIs, Indeed APIs, ZipRecruiter Partner Platform.
- Public feeds/pages: require source policy approval, robots.txt checks, sitemap/JobPosting alignment, and conservative rate limits.
- Unsupported/risky scraping: disabled; skip source and log policy decision.

Important source notes:

- Greenhouse documents a public Job Board API for published jobs.
- Lever publishes a Postings API for company job sites.
- Google documents `JobPosting` structured data and warns against expired/spam/misleading jobs.
- LinkedIn job APIs are partner/Talent Solutions oriented and should not be replaced with scraping.
- Indeed APIs are governed by partner/OAuth terms and written agreements.

## Step-by-Step Integration Plan

1. Keep current Flask upload route working.
2. Add the current starter package and result-page recommendations.
3. Add user accounts and persist resumes/profiles/jobs.
4. Move `run_job_automation` from request-time to Celery background task.
5. Add Greenhouse and Lever source configuration.
6. Add email provider and notification table.
7. Build dashboard filters and job state actions.
8. Add embedding similarity and vector storage.
9. Add source audit dashboard for compliance.
10. Add future modules: cover letters, interview prep, ATS auto-apply only through official apply APIs.

## Future Features

- ATS auto-apply: only via official apply endpoints or partner programs, never credential-sharing or unauthorized browser automation.
- Cover letter generation: use matched job explanation and missing skills.
- Interview preparation: generate questions from job description and resume projects.
- Recruiter outreach: create personalized messages with user approval.
