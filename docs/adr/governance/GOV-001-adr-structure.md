# GOV-001: Architecture Decision Record Structure

**Status:** Accepted  
**Date:** 2026-02-04  
**Author:** Wolfram Laube  
**Tags:** governance, documentation, architecture

## Context

The `blauweiss_llc` GitLab group has grown to include multiple repositories with different purposes:

| Repo | Purpose |
|------|---------|
| `projects/clarissa` | AI/NLP Research (Bachelor thesis) |
| `ops/backoffice` | Business operations (billing, timesheets, applications) |
| `ops/crm` | CRM system (GitLab Issues as database) |
| `ops/corporate` | Company-wide assets (legal, identity, finance) |

Architecture Decision Records (ADRs) have accumulated in different locations:
- **CLARISSA:** 30 ADRs (ADR-001 to ADR-030), well-maintained
- **Backoffice:** 1 ADR (ADR-030), numbering conflict with CLARISSA

### Problems

1. **Numbering collision:** ADR-030 exists in two repos with different content
2. **Cross-cutting decisions:** Some ADRs (e.g., billing, deployment) span multiple repos
3. **Discoverability:** No single place to find all architectural decisions
4. **Domain confusion:** Research decisions mixed with operations decisions

## Decision

### 1. Centralize ADRs in `ops/corporate/docs/adr/`

All ADRs live in one location, organized by domain subdirectories:

```
ops/corporate/docs/adr/
├── index.md                    # Master index of all ADRs
├── _template.md                # ADR template
│
├── governance/                 # GOV-xxx: Company-wide decisions
│   ├── GOV-001-adr-structure.md
│   └── GOV-002-repo-responsibilities.md
│
├── research/                   # RES-xxx: CLARISSA, AI/ML, academic
│   ├── RES-001-physics-centric.md
│   └── ...
│
├── operations/                 # OPS-xxx: Billing, CRM, workflows
│   ├── OPS-001-billing-migration.md
│   └── ...
│
└── infrastructure/             # INF-xxx: Runners, GCP, K8s, CI/CD
    ├── INF-001-runner-strategy.md
    └── ...
```

### 2. Domain Prefixes

| Prefix | Domain | Scope | Examples |
|--------|--------|-------|----------|
| **GOV** | Governance | Cross-cutting, org-wide | ADR structure, repo ownership |
| **RES** | Research | CLARISSA, ML/AI, Bachelor | NLP pipeline, physics engine |
| **OPS** | Operations | Backoffice, CRM, billing | Invoicing workflow, CRM schema |
| **INF** | Infrastructure | CI/CD, runners, cloud | GCP setup, K8s deployment |

### 3. Numbering Rules

- Each domain starts at 001
- Numbers are never reused (even if ADR is superseded)
- Format: `{PREFIX}-{NNN}-{slug}.md` (e.g., `OPS-001-billing-migration.md`)

### 4. Migration Plan

| Source | Target | Action |
|--------|--------|--------|
| CLARISSA ADR-001 to ADR-015 | RES-001 to RES-015 | Rename, move |
| CLARISSA ADR-016 to ADR-023 | INF-001 to INF-008 | Rename, move (infra-related) |
| CLARISSA ADR-024 to ADR-030 | RES-016 to RES-022 | Rename, move |
| Backoffice ADR-030 | OPS-001 | Rename, move |

Migration will happen incrementally. Original files get a deprecation notice pointing to new location.

## Consequences

### Positive

- **Single source of truth:** One place to find all decisions
- **No collisions:** Domain prefixes prevent numbering conflicts
- **Clear ownership:** Prefix immediately identifies domain
- **Scalable:** New domains = new prefix
- **Searchable:** `grep "OPS-"` finds all operations decisions

### Negative

- **Migration effort:** ~30 files need renaming and moving
- **Link updates:** Internal references need updating
- **Learning curve:** Team needs to know prefixes

### Neutral

- ADRs that span domains get primary prefix based on main impact
- Cross-references use full ID (e.g., "See also INF-003")

## Related

- GOV-002: Repository Responsibilities (planned)
- CLARISSA `docs/architecture/adr/` (to be migrated)
- Backoffice `docs/adr/` (to be migrated)
