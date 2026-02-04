# OPS-003: Runbook Structure

**Status:** Proposed  
**Date:** 2026-02-04  
**Author:** Wolfram Laube  
**Tags:** operations, documentation, runbook, workflows  

## Context

The blauweiss_llc operations span multiple repositories, CI pipelines, scheduled jobs, and manual workflows. Currently:

- Documentation is scattered across handover documents, README files, and tribal knowledge
- No single source of truth for "how do I do X?"
- New team members (Ian, Michael) have no onboarding path
- Even the owner forgets which button to push after 2 weeks away

### Pain Points

| Problem | Example |
|---------|---------|
| **Where is X?** | "Is billing in CLARISSA or backoffice?" |
| **How do I trigger Y?** | "What variables does the applications pipeline need?" |
| **When does Z run?** | "Is there a schedule for CRM integrity checks?" |
| **What if it fails?** | "The billing pipeline failed - now what?" |

### Requirements

1. **Deppensicher** (foolproof) - Anyone can follow without prior knowledge
2. **Single source of truth** - One place for all operational procedures
3. **Searchable** - Find answers in <30 seconds
4. **Maintainable** - Easy to update when things change
5. **Linked from Portal** - Accessible via web UI

## Decision

**Create a structured Runbook in `ops/backoffice/docs/runbook/` with standardized format.**

### Runbook Location

```
ops/backoffice/
└── docs/
    └── runbook/
        ├── index.md              # Overview + quick links
        ├── billing.md            # Zeiterfassung → Rechnung
        ├── applications.md       # Jobsuche-Pipeline
        ├── crm.md                # CRM Workflows
        ├── timesheets.md         # Zeit erfassen
        ├── invoicing.md          # Rechnungen erstellen
        └── troubleshooting.md    # Wenn's brennt
```

### Standard Runbook Entry Format

Each workflow gets a consistent structure:

```markdown
# {Workflow Name}

> One-sentence description of what this does.

## Quick Reference

| Item | Value |
|------|-------|
| **Repo** | ops/backoffice |
| **Pipeline** | `.gitlab/billing.yml` |
| **Schedule** | #4094512 (1. des Monats, 06:00) |
| **Trigger URL** | [Portal → Billing](https://...) |
| **Owner** | Wolfram |

## Prerequisites

- [ ] Checklist of what must be true before starting

## Happy Path (Normal Flow)

### Step 1: {Action}

{Detailed instructions with screenshots/commands}

### Step 2: {Action}

...

## Variations

### Scenario A: {Different situation}

{How to handle}

### Scenario B: {Another situation}

{How to handle}

## Troubleshooting

### Error: {Common error}

**Symptom:** What you see  
**Cause:** Why it happens  
**Fix:** How to resolve  

## Related

- [OPS-001: Billing Migration](../adr/operations/OPS-001-billing-migration.md)
- [CRM Runbook](crm.md)
```

### Workflow Categories

| Category | Runbook | Key Workflows |
|----------|---------|---------------|
| **Billing** | `billing.md` | Time tracking, timesheet generation, invoicing, upload |
| **Applications** | `applications.md` | Crawl, match, draft, send, CRM update |
| **CRM** | `crm.md` | Create issue, update status, integrity check |
| **Timesheets** | `timesheets.md` | GitLab /spend, corrections, reports |
| **Infrastructure** | `infra.md` | Runner setup, GCP, fallback |

### Portal Integration

Each runbook links to/from the Operations Portal:

```
Portal (docs/portal.html)
    │
    ├── [Billing] → Trigger Button → Pipeline
    │      └── [?] → runbook/billing.md
    │
    ├── [Applications] → Trigger Button → Pipeline  
    │      └── [?] → runbook/applications.md
    │
    └── [CRM] → Board Link
           └── [?] → runbook/crm.md
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Runbook file | `{domain}.md` | `billing.md` |
| Section headers | Title Case | `## Quick Reference` |
| Commands | Code blocks with shell | ` ```bash ` |
| Links | Relative paths | `[CRM](crm.md)` |
| Screenshots | `assets/{domain}-{step}.png` | `assets/billing-trigger.png` |

## Consequences

### Positive

- ✅ **Onboarding:** New team members self-serve
- ✅ **Consistency:** Same format everywhere
- ✅ **Discoverability:** Portal links to relevant runbook
- ✅ **Maintenance:** Update one place, not five handovers
- ✅ **Troubleshooting:** Known issues documented

### Negative

- ⚠️ **Initial effort:** Need to write all runbooks
- ⚠️ **Maintenance burden:** Must keep in sync with code changes
- ⚠️ **Duplication risk:** ADRs describe "why", runbooks describe "how"

### Mitigations

| Risk | Mitigation |
|------|------------|
| Runbooks go stale | CI job checks for broken links |
| Too much duplication | ADRs link to runbooks, not vice versa |
| Nobody reads them | Portal has prominent "How do I...?" section |

## Implementation

1. Create `docs/runbook/` directory structure
2. Write `index.md` with overview
3. Write `billing.md` (most complex, good template)
4. Write remaining runbooks
5. Add links from Portal
6. Add "last updated" timestamps

## Related

- GOV-001: ADR Structure
- OPS-001: Billing Migration
- [Operations Portal](../portal.html)
- [Quick Start Guide](../ops/quickstart.md)
