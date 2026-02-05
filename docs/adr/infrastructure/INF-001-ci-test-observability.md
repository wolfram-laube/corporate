# INF-001: CI/CD Test Observability

**Status:** Accepted  
**Date:** 2026-02-05  
**Author:** Wolfram Laube  
**Tags:** ci-cd, observability, metrics, testing, cloud-run  
**Supersedes:** —  
**Superseded by:** —

## Context

All CI/CD test suites (217+ tests across `test:unit`, `test:nsai:unit`, `test:nsai:notebooks`, `test:coverage`) generate JUnit XML reports and log output. Currently these artifacts are:

- **JUnit XMLs**: Stored as GitLab artifacts with 7–30 day TTL, then lost
- **Job Traces**: Available via GitLab API while jobs exist, no structured indexing
- **Coverage Reports**: HTML artifacts, 30 day TTL
- **Trend Data**: None — no historical view of test health, flake rates, or performance regression

There is no way to answer questions like "how has test duration evolved over the last 3 months?" or "which tests have the highest flake rate?" without manually querying the GitLab API for each pipeline.

## Decision

Implement a **lightweight Cloud Run metrics collector** (Option B) that captures test metrics after each pipeline run and stores them for trend analysis.

### Architecture

```
GitLab CI Pipeline
       │
       ▼
  [test:unit]  [test:nsai:unit]  [test:nsai:notebooks]
       │              │                    │
       ▼              ▼                    ▼
   report.xml     report.xml          report.xml
       │              │                    │
       └──────────────┼────────────────────┘
                      ▼
          [ci-metrics:collect]  ← Post-test CI job
                      │
                      ▼
          Cloud Run: ci-metrics-collector
                      │
                      ▼
              BigQuery / Firestore
                      │
                      ▼
              Grafana Cloud (Free Tier)
              or GCP Cloud Monitoring
```

### What Gets Collected

| Metric | Source | Type |
|--------|--------|------|
| Tests passed/failed/skipped | JUnit XML | Counter |
| Test duration (per suite) | JUnit XML | Gauge |
| Test duration (per test) | JUnit XML | Gauge |
| Pipeline duration | GitLab API | Gauge |
| Coverage % | pytest-cov | Gauge |
| Flake rate | historical comparison | Derived |

### Storage

- **Primary:** BigQuery (free tier: 1TB query/month, 10GB storage)
- **Alternative:** Firestore (free tier: 1GB storage, 50K reads/day)
- **Backup:** CSV/JSON in GCS bucket for raw data

## Consequences

### Positive

- Historical trend visibility for test health
- Early detection of test performance regression
- Flake rate tracking enables targeted test fixes
- Low operational cost (Cloud Run + BigQuery free tiers)
- Portfolio showcase for DevOps/SRE positioning

### Negative

- Additional CI job adds ~10s to pipeline
- Another Cloud Run service to maintain
- BigQuery schema evolution needs care

### Neutral

- JUnit XML artifacts still expire per GitLab retention — metrics survive independently

## Alternatives Considered

| Alternative | Pros | Cons | Why Not (Now) |
|-------------|------|------|---------------|
| **A: GitLab-native only** | Zero infra, free, JUnit reports in MRs | No historical trends, no dashboards, 7-day artifact TTL | Insufficient for trend analysis |
| **B: Cloud Run collector** ✅ | Low cost, fits existing GCP infra, lightweight, scalable | Small maintenance overhead | **Selected** |
| **C: Full Prometheus + Grafana + Loki** | Industry-standard, powerful querying, log aggregation | Overkill for current team size, significant infra/cost overhead, needs persistent storage | Deferred — reassess when team grows or >500 tests |

### Upgrade Path: B → C

Option B is designed as a stepping stone. When the need arises:
1. Cloud Run collector already produces structured metrics → easy to add Prometheus `/metrics` endpoint
2. BigQuery data can be exported to Prometheus via adapter
3. Grafana Cloud free tier already supports Prometheus datasources
4. Loki can be added incrementally for log aggregation

## Implementation

- [ ] Cloud Run service `ci-metrics-collector` (Python/FastAPI)
  - POST `/ingest` — accepts JUnit XML + pipeline metadata
  - GET `/metrics` — Prometheus-compatible endpoint (future-proofing)
  - GET `/health` — health check
- [ ] BigQuery dataset `ci_metrics` with tables:
  - `test_runs` (pipeline_id, job, suite, passed, failed, skipped, duration)
  - `test_cases` (pipeline_id, job, test_name, status, duration)
- [ ] CI job `ci-metrics:collect` in `.gitlab/tests.yml`
  - Runs after test jobs, parses JUnit XMLs, POSTs to collector
- [ ] Dashboard (Grafana Cloud free tier or GCP Cloud Monitoring)
  - Test pass rate over time
  - Duration trends per suite
  - Flake rate leaderboard
- [ ] Update this ADR status after deployment

## Related

### Internal
- [GOV-002: Notebook Standards](../governance/GOV-002-notebook-standards.md) — notebook tests are a data source
- [OPS-001: Billing Migration](../operations/OPS-001-billing-migration.md) — billing tests are a data source
- [AI-001: Neurosymbolic Runner Selection](../ai/AI-001-neurosymbolic-runner-selection.md) — NSAI tests are a data source
- ops/backoffice Issue #37 — Implementation backlog

### External
- [GitLab JUnit Reports](https://docs.gitlab.com/ee/ci/testing/unit_test_reports.html)
- [BigQuery Free Tier](https://cloud.google.com/bigquery/pricing#free-tier)
- [Grafana Cloud Free](https://grafana.com/pricing/)
