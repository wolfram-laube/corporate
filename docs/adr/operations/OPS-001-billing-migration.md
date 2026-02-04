# OPS-001: Billing System Migration (CLARISSA → Backoffice)

**Status:** Proposed  
**Date:** 2026-02-04  
**Author:** Wolfram Laube  
**Tags:** operations, billing, migration, architecture  
**Supersedes:** Partially supersedes CLARISSA ADR-019 (Billing Folder Structure)

## Context

The billing system currently resides in the **CLARISSA** repository (`projects/clarissa`), which is designated for AI/NLP research. This creates several problems:

### Current State

```
projects/clarissa/ (77260390)
├── billing/
│   ├── config/
│   │   ├── clients.yaml          # Client definitions, rates
│   │   └── sequences.yaml        # Invoice number sequences
│   ├── scripts/
│   │   ├── generate_timesheet.py # GraphQL API for time entries
│   │   ├── generate_invoice.py   # Consolidation + Typst rendering
│   │   └── upload_to_drive.py    # Google Drive upload
│   ├── templates/
│   │   ├── timesheet.typ         # Typst timesheet template
│   │   ├── rechnung-de.typ       # German invoice
│   │   └── invoice-en-eu.typ     # EU invoice (reverse charge)
│   └── output/                   # Generated artifacts
│
├── research/                     # ← This is what CLARISSA should be
├── notebooks/
└── ...
```

### Problems

| Problem | Impact |
|---------|--------|
| **Wrong repo** | Billing is business ops, not research |
| **Confused CI/CD** | Research pipelines mixed with billing jobs |
| **Credential sprawl** | OAuth tokens for billing in research repo |
| **Duplicate code** | `backoffice/modules/invoicing/` exists separately |
| **ADR confusion** | ADR-019 (billing structure) lives in research repo |

### What Works (Don't Break)

- ✅ Scheduled pipeline: 1st of month, 06:00 Vienna (Schedule #4094512)
- ✅ Time tracking via GitLab `/spend` commands
- ✅ GraphQL API for accurate `spentAt` dates
- ✅ Typst → PDF generation
- ✅ Google Drive upload to shared drive
- ✅ Multi-consultant support (Wolfram, Ian)

## Decision

**Migrate `billing/` from CLARISSA to `ops/backoffice/modules/billing/`.**

### Target Structure

```
ops/backoffice/ (77555895)
├── modules/
│   ├── billing/                  # ← MIGRATED FROM CLARISSA
│   │   ├── config/
│   │   │   ├── clients.yaml
│   │   │   └── sequences.yaml
│   │   ├── scripts/
│   │   │   ├── generate_timesheet.py
│   │   │   ├── generate_invoice.py
│   │   │   └── upload_to_drive.py
│   │   ├── templates/
│   │   │   ├── timesheet.typ
│   │   │   ├── rechnung-de.typ
│   │   │   └── invoice-en-eu.typ
│   │   └── output/
│   │
│   ├── timesheets/               # ← MERGE/DEPRECATE (uses YAML, redundant)
│   ├── invoicing/                # ← MERGE/DEPRECATE (partial implementation)
│   ├── applications/
│   ├── controlling/
│   └── tax/
│
├── .gitlab/
│   └── billing.yml               # ← UPDATE: paths, project references
│
└── config/google/
    └── credentials.json          # Already exists, reuse
```

### Migration Steps

| Step | Task | Effort |
|------|------|--------|
| 1 | Copy `billing/` from CLARISSA → backoffice | 15 min |
| 2 | Update import paths in Python scripts | 30 min |
| 3 | Update `.gitlab/billing.yml` in backoffice | 30 min |
| 4 | Migrate Schedule #4094512 to backoffice project | 15 min |
| 5 | Verify Google Drive credentials work | 15 min |
| 6 | Run test billing cycle | 30 min |
| 7 | Delete `billing/` from CLARISSA + add redirect notice | 15 min |
| 8 | Deprecate `modules/timesheets/` and `modules/invoicing/` | 15 min |

**Total estimated effort: 3 hours**

### What Gets Deprecated

| Path | Reason |
|------|--------|
| `backoffice/modules/timesheets/` | Uses YAML files; we use GitLab /spend |
| `backoffice/modules/invoicing/` | Partial duplicate; merged into billing/ |
| `clarissa/billing/` | Moved to backoffice |

### Credential Handling

| Credential | Current Location | Action |
|------------|------------------|--------|
| Google OAuth (Drive) | CLARISSA `config/google/` | Already in backoffice, reuse |
| GitLab PAT | CI variable | Works across projects |
| Service Account | CI variable | Move to backoffice CI vars |

## Consequences

### Positive

- ✅ **Clean separation:** Research repo = research only
- ✅ **Single billing codebase:** No more duplicates
- ✅ **Logical grouping:** Billing next to timesheets, invoicing, controlling
- ✅ **Simpler CI/CD:** Billing pipeline only in ops repo
- ✅ **ADR alignment:** OPS-001 lives in ops, not research

### Negative

- ⚠️ **Migration effort:** 3 hours of careful work
- ⚠️ **Schedule migration:** Need to recreate in new project
- ⚠️ **Testing required:** Must verify full cycle works

### Neutral

- Time tracking via `/spend` unchanged
- Google Drive folder structure unchanged
- Invoice numbering continues from current sequence

## Alternatives Considered

| Alternative | Pros | Cons | Why Not |
|-------------|------|------|---------|
| Leave in CLARISSA | No effort | Violates separation of concerns | Architectural debt grows |
| Create new `ops/billing` repo | Maximum isolation | Yet another repo; overkill | Backoffice already has modules/ |
| Symlink/submodule | Quick "fix" | Fragile, confusing | Not a real solution |

## Implementation Checklist

- [x] Create `modules/billing/` in backoffice
- [x] Copy scripts, templates, config from CLARISSA
- [x] Update Python imports (paths only) (`from billing.` → `from modules.billing.`)
- [x] Update `.gitlab/billing.yml` paths
- [x] Create new Schedule (#4126476) in backoffice (same cron: `0 6 1 * *`)
- [x] Add CI variables (BILLING_RUN): `GOOGLE_CREDENTIALS`, `GDRIVE_FOLDER_ID`
- [ ] Test: Generate timesheet for test period
- [ ] Test: Generate invoice for test period
- [ ] Test: Upload to Google Drive
- [ ] Delete CLARISSA `billing/` (after verification) folder
- [x] Add deprecation notice in CLARISSA README
- [x] Archive `modules/timesheets/` (DEPRECATED.md added) and `modules/invoicing/`
- [x] Update this ADR status to "Accepted"

## Related

- GOV-001: ADR Structure
- CLARISSA ADR-019: Billing Folder Structure (superseded by this)
- CLARISSA ADR-017: GDrive Folder Structure (still valid)
- Backoffice Schedule #4094512 (to be migrated)
- Google Drive: BLAUWEISS-EDV-LLC shared drive

---

## Migration Log (2026-02-04)

### Completed Steps

| Step | Commit | Details |
|------|--------|---------|
| 1. Copy config | `02f573c3` | clients.yaml, sequences.yaml, README, CONVENTIONS |
| 2. Copy scripts | `63cfa9d0` | 6 Python scripts |
| 3. Copy templates | `ef5679a3` | 4 Typst templates + logo |
| 4. Update CI | (update) | .gitlab/billing.yml paths updated |
| 5. Create Schedule | #4126476 | 1st of month, 06:00 Vienna |
| 6. Deactivate old | #4094512 | CLARISSA schedule disabled |
| 7. Deprecation notices | `315f1a9f` | timesheets/, invoicing/ marked |
| 8. CLARISSA notice | (update) | billing/README.md updated |

### Pending

- [ ] Test billing cycle (wait for next month or manual trigger)
- [ ] Verify Google Drive credentials work in backoffice
- [ ] Delete CLARISSA billing/ folder (after successful test)

### New Schedule Details

- **Project:** ops/backoffice (77555895)
- **Schedule ID:** 4126476
- **Cron:** `0 6 1 * *` (1st of month, 06:00 Vienna)
- **Variable:** `BILLING_RUN=true`
