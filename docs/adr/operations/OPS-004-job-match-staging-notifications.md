# OPS-004: Job Match Staging & Multi-Channel Notification Service

**Status:** Proposed
**Date:** 2026-02-08
**Author:** Wolfram Laube + Claude
**Deciders:** Wolfram Laube

## Context

The Search → Match → Draft cycle for job applications currently runs as a synchronous,
conversational process in Claude. Matched leads go directly into draft state without a
review gate. This has several problems:

1. **No review gate** — Matches are drafted and delivered immediately, no staging area
2. **No persistence** — Match results live only in the chat context
3. **No async notification** — User must be actively in session to see results
4. **No audit trail** — No record of which matches were reviewed, approved, or rejected

## Decision

Build a **Job Match Staging & Notification Service** ("Vorhölle") with:

1. **Staging via GitLab Issues** — Each match becomes a GitLab Issue in backoffice repo
2. **Multi-Channel Notifications** — Configurable alerts via Email, Slack, WhatsApp, GitLab ToDo
3. **Review Workflow** — Label-based state machine: `pending` → `approved`/`rejected` → `sent`
4. **Attachments** — CV, Profil, Draft are attached to the staging issue

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Session                        │
│  Search → Match Engine (≥70% threshold)                  │
│         │                                                │
│         ▼                                                │
│  POST /api/v1/matches                                    │
└─────────┬───────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│            Match Staging Service (FastAPI)                │
│            Cloud Run: match-staging-service               │
│                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │ GitLab   │   │ Notification │   │ Config Manager  │  │
│  │ Adapter  │   │ Dispatcher   │   │ (YAML/env)      │  │
│  │          │   │              │   │                 │  │
│  │ • Issue  │   │ • Email      │   │ • channels[]    │  │
│  │ • Labels │   │ • Slack      │   │ • threshold     │  │
│  │ • Notes  │   │ • WhatsApp   │   │ • templates     │  │
│  │ • Upload │   │ • GitLab ToDo│   │ • quiet_hours   │  │
│  └──────────┘   └──────────────┘   └─────────────────┘  │
│                                                          │
│  Endpoints:                                              │
│  POST /api/v1/matches          → Stage new match(es)     │
│  GET  /api/v1/matches          → List staged matches     │
│  PATCH /api/v1/matches/{id}    → Approve/Reject          │
│  POST /api/v1/matches/{id}/send → Trigger send           │
│  GET  /api/v1/config           → Current notification cfg│
│  PUT  /api/v1/config           → Update notification cfg │
└─────────────────────────────────────────────────────────┘
```

### Notification Channels

| Channel     | Implementation                | Payload              | Config Required          |
|-------------|-------------------------------|----------------------|--------------------------|
| **Email**   | Gmail API (existing creds)    | HTML summary + links | `email.recipients[]`     |
| **Slack**   | Incoming Webhook              | Rich message block   | `slack.webhook_url`      |
| **WhatsApp**| Twilio WhatsApp Business API  | Text + link          | `whatsapp.twilio_*`      |
| **GitLab**  | ToDo API + Issue assignment   | Issue link           | `gitlab.assignee_id`     |

### GitLab Issue Structure

```yaml
Title: "[JOB-MATCH] {score}% — {project_title}"
Labels:
  - job-match
  - job-match/pending          # Initial state
  - match-score/{high|medium}  # ≥90% = high, 70-89% = medium
Description: |
  ## Match Details
  - **Score:** {score}%
  - **Provider:** {provider}
  - **Location:** {location}
  - **Start:** {start} | **Duration:** {duration}
  - **Rate:** {rate} EUR/h
  - **URL:** {url}

  ## Score Breakdown
  {requirements_table}

  ## Notes
  {match_notes}

  ## Draft
  {anschreiben_text}
Attachments:
  - Profil_Laube_w_Summary_DE.pdf
  - CV (if customized)
```

### State Machine

```
                    ┌─────────┐
         create ──▶ │ pending │
                    └────┬────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        ┌──────────┐         ┌──────────┐
        │ approved │         │ rejected │
        └────┬─────┘         └──────────┘
             │
             ▼ (manual trigger or auto)
        ┌──────────┐
        │   sent   │
        └──────────┘
```

Label transitions:
- `job-match/pending` → `job-match/approved` (user approves via UI or API)
- `job-match/pending` → `job-match/rejected` (user rejects)
- `job-match/approved` → `job-match/sent` (application submitted)

### User Configuration

```yaml
# config/notification-channels.yml
notification:
  channels:
    email:
      enabled: true
      recipients:
        - wolfram.laube@blauweiss-edv.at
      template: "match_summary"   # HTML template name
    slack:
      enabled: false
      webhook_url: ""             # Incoming webhook URL
      channel: "#job-matches"
    whatsapp:
      enabled: false
      provider: "twilio"
      account_sid: ""
      auth_token: ""
      from_number: ""             # Twilio WhatsApp number
      to_number: "+436644011521"
    gitlab_todo:
      enabled: true
      assignee_id: 1349601        # wolfram.laube

  preferences:
    threshold: 70                 # Minimum match score to stage
    quiet_hours:                  # Don't notify between
      start: "22:00"
      end: "07:00"
      timezone: "Europe/Vienna"
    batch_mode: true              # Batch notifications per cycle
    batch_summary: true           # Single summary vs. per-match
```

### Notification Payload

```json
{
  "cycle_id": "2026-02-08T14:30:00Z",
  "matches_count": 5,
  "matches": [
    {
      "score": 97,
      "title": "Cloud Architect - Cloud-Transformation",
      "provider": "Amoria Bond GmbH",
      "location": "Heilbronn (100% Remote)",
      "start": "ASAP",
      "duration": "3 Mo+",
      "issue_url": "https://gitlab.com/wolfram.laube/backoffice/-/issues/XX",
      "source_url": "https://www.freelancermap.de/projekt/..."
    }
  ],
  "summary": "5 neue Matches: 🔥 97% Cloud Arch, 🔥 95% Platform Eng, 🔥 93% GCP DevOps, 🔥 91% K8s D4A, ✅ 83% Energy IoT"
}
```

#### Email Template (HTML)

Subject: `[Blauweiss] 5 neue Job-Matches — Top: 97% Cloud Architect`

#### Slack Message

```
🎯 *5 neue Job-Matches*
├ 🔥 97% Cloud Architect (Amoria Bond) — Heilbronn Remote
├ 🔥 95% Platform-Engineer (Westhouse) — FFM/Remote
├ 🔥 93% DevOps GCP (C4 Energy) — Remote 12Mo
├ 🔥 91% K8s D4A (Nemensis) — FFM/Berlin 6Mo+
└ ✅ 83% Energy IoT (GULP) — Essen 7Mo
👉 Review: https://gitlab.com/.../issues?label=job-match/pending
```

#### WhatsApp Message

```
🎯 5 neue Job-Matches!
Top: 97% Cloud Architect (Remote, ASAP)
Review: https://gitlab.com/.../issues?label=job-match/pending
```

### Tech Stack

| Component         | Technology                          |
|-------------------|-------------------------------------|
| Service           | Python 3.12, FastAPI                |
| Hosting           | GCP Cloud Run (existing pipeline)   |
| Config            | YAML in repo + env var overrides    |
| Email             | Gmail API (credentials.json exists) |
| Slack             | requests → Incoming Webhook         |
| WhatsApp          | twilio SDK                          |
| GitLab            | python-gitlab / REST API            |
| Templates         | Jinja2                              |
| Container         | Docker (multi-stage, <100MB)        |

### Integration Points

- **Existing:** Gmail credentials (`credentials.json` in project)
- **Existing:** GitLab PAT (backoffice repo access)
- **Existing:** Cloud Run deployment pipeline (MAB service as template)
- **New:** Slack workspace + Incoming Webhook
- **New:** Twilio account for WhatsApp Business

### File Structure (backoffice repo)

```
services/
  match-staging/
    Dockerfile
    pyproject.toml
    src/
      main.py                 # FastAPI app
      config.py               # Config loader (YAML + env)
      models.py               # Pydantic models
      adapters/
        gitlab_adapter.py     # Issue creation, labels, uploads
        email_adapter.py      # Gmail API sender
        slack_adapter.py      # Webhook sender
        whatsapp_adapter.py   # Twilio sender
        gitlab_todo.py        # ToDo API
      templates/
        email_summary.html    # Jinja2 email template
        slack_block.json      # Slack Block Kit template
      dispatcher.py           # Notification orchestrator
    config/
      notification-channels.yml
    tests/
      test_adapters.py
      test_dispatcher.py
      test_staging.py
```

## Consequences

### Positive
- Review gate prevents accidental/bad applications
- Async workflow — matches accumulate, user reviews when ready
- Full audit trail in GitLab Issues
- Multi-channel ensures user gets notified regardless of context
- Extensible — new channels (Telegram, Teams) are just new adapters
- Reusable — same notification infra can serve billing alerts, CI alerts, etc.

### Negative
- Additional service to maintain (Cloud Run cost: ~$0/month at low volume)
- Twilio costs for WhatsApp (~$0.005/message, negligible)
- Slack workspace setup if not already existing

### Risks
- WhatsApp Business API approval can take time → start with Email + GitLab ToDo
- Quiet hours logic adds complexity → implement in v2

## Implementation Plan

| Phase | What                                      | Effort  |
|-------|-------------------------------------------|---------|
| v0.1  | GitLab Issue creation + GitLab ToDo       | 2h      |
| v0.2  | Email notification (Gmail API)            | 2h      |
| v0.3  | Slack webhook                             | 1h      |
| v0.4  | Cloud Run deployment                      | 1h      |
| v0.5  | WhatsApp via Twilio                       | 2h      |
| v1.0  | Config UI, quiet hours, batch mode        | 4h      |

Total MVP (v0.1–v0.4): ~6h
Full service (v1.0): ~12h

## Related

- OPS-001: Billing Migration (similar service pattern)
- AI-001: Neurosymbolic Runner Selection (MAB Cloud Run deployment as template)
- GOV-003: Publication Workflow (Quarto pipeline pattern)