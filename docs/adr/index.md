# Architecture Decision Records

> Central repository for all architectural decisions across the blauweiss_llc organization.

## Quick Reference

| Prefix | Domain | Count | Description |
|--------|--------|-------|-------------|
| [GOV](#governance) | Governance | 2 | Organization-wide decisions |
| [AI](#ai--machine-learning) | AI / ML | 1 | Neurosymbolic AI, Runner Selection |
| [RES](#research) | Research | 0* | CLARISSA, AI/ML, academic |
| [OPS](#operations) | Operations | 2 | Billing, CRM, workflows |
| [INF](#infrastructure) | Infrastructure | 1 | Runners, GCP, CI/CD |

*Migration from CLARISSA pending

---

## Governance (GOV)

Cross-cutting decisions affecting the entire organization.

| ID | Title | Status | Date |
|----|-------|--------|------|
| [GOV-001](governance/GOV-001-adr-structure.md) | ADR Structure | ✅ Accepted | 2026-02-04 |
| [GOV-002](governance/GOV-002-notebook-standards.md) | Jupyter Notebook Standards | ✅ Accepted | 2026-02-05 |
| GOV-003 | Repository Responsibilities | 📋 Planned | - |

**Templates:** [`docs/templates/notebook-template.ipynb`](../templates/notebook-template.ipynb)

---

## AI / Machine Learning

Artificial Intelligence, Machine Learning, Neurosymbolic Systems.

| ID | Title | Status | Date |
|----|-------|--------|------|
| [AI-001](ai/AI-001-neurosymbolic-runner-selection.md) | Neurosymbolic Runner Selection | ✅ Accepted | 2026-02-05 |

**Related:** ops/backoffice Epic #27, JKU AI Bachelor Thesis (#26)

---

## Research (RES)

CLARISSA project, AI/NLP research, academic work.

| ID | Title | Status | Date |
|----|-------|--------|------|
| *Migration pending from CLARISSA ADR-001 to ADR-030* |

---

## Operations (OPS)

Business operations: billing, invoicing, timesheets, CRM, applications.

| ID | Title | Status | Date |
|----|-------|--------|------|
| [OPS-001](operations/OPS-001-billing-migration.md) | Billing Migration | ✅ Accepted | 2026-02-04 |
| [OPS-003](operations/OPS-003-runbook-structure.md) | Runbook Structure | ✅ Accepted | 2026-02-04 |
| OPS-002 | CRM GitLab Issues | 📋 Planned | - |

---

## Infrastructure (INF)

CI/CD pipelines, GitLab runners, cloud infrastructure, Kubernetes.

| ID | Title | Status | Date |
|----|-------|--------|------|
| [INF-001](infrastructure/INF-001-ci-test-observability.md) | CI/CD Test Observability | ✅ Accepted | 2026-02-05 |
| *Migration pending from CLARISSA infrastructure ADRs* |

---

## Status Legend

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | Accepted | Decision is in effect |
| 📋 | Planned | Identified but not written |
| 🔄 | Proposed | Under discussion |
| ⚠️ | Deprecated | Superseded by another ADR |
| ❌ | Rejected | Decision was not adopted |

---

## Contributing

1. Copy `_template.md` to the appropriate domain folder
2. Use the naming convention: `{PREFIX}-{NNN}-{slug}.md`
3. Fill out all sections
4. Submit MR for review
5. Update this index after merge

### Templates

- **ADR:** [`_template.md`](./_template.md)
- **Notebook:** [`docs/templates/notebook-template.ipynb`](../templates/notebook-template.ipynb)
