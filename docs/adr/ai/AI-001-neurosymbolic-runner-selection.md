# AI-001: Neurosymbolic Runner Selection Architecture

**Status:** Accepted  
**Date:** 2026-02-04 (Updated: 2026-02-05)  
**Author:** Wolfram Laube  
**Tags:** ai/ml, neurosymbolic-ai, reinforcement-learning, ci/cd, jku-bachelor  
**Supersedes:** —  
**Superseded by:** —

## Context

Die GitLab CI/CD-Infrastruktur nutzt mehrere Runner mit unterschiedlichen Capabilities (Docker, Shell, GPU, verschiedene Cloud-Regionen). Die aktuelle Runner-Zuweisung erfolgt statisch über Tags, was zu suboptimaler Ressourcennutzung führt:

- **Problem 1:** Keine Adaption an Runner-Performance-Schwankungen
- **Problem 2:** Keine Berücksichtigung von Job-Charakteristiken bei der Auswahl
- **Problem 3:** Keine Lernfähigkeit aus historischen Ausführungsdaten

Der Multi-Armed Bandit (MAB) Ansatz (#28) adressiert das Exploration-Exploitation-Dilemma, ignoriert aber strukturiertes Wissen über Runner-Capabilities und Job-Requirements.

## Decision

Wir implementieren eine **zweistufige Neurosymbolic AI Architektur**:

### Symbolische Ebene (Knowledge Layer)

```
┌─────────────────────────────────────────────────────┐
│                 SYMBOLIC LAYER                       │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────────────┐     │
│  │   Runner    │    │    Job Requirement      │     │
│  │  Ontology   │───▶│       Parser            │     │
│  │  (OWL/RDF)  │    │   (.gitlab-ci.yml)      │     │
│  └─────────────┘    └───────────┬─────────────┘     │
│         │                       │                   │
│         ▼                       ▼                   │
│  ┌─────────────────────────────────────────────┐   │
│  │       Constraint Satisfaction Problem        │   │
│  │   (Runner ∩ Job.requirements ≠ ∅)           │   │
│  └─────────────────────────────────────────────┘   │
│                       │                             │
│                       ▼                             │
│              [Feasible Runner Set]                  │
└─────────────────────────────────────────────────────┘
```

**Komponenten:**
- **Runner Capability Ontology** (#22): OWL-basierte Beschreibung von Runner-Eigenschaften
- **Job Requirement Parser** (#23): Extraktion von Requirements aus `.gitlab-ci.yml`
- **Constraint Satisfaction Module** (#24): Pruning infeasibler Runner

### Subsymbolische Ebene (Learning Layer)

```
┌─────────────────────────────────────────────────────┐
│               SUBSYMBOLIC LAYER                      │
├─────────────────────────────────────────────────────┤
│  Input: Feasible Runner Set (from Symbolic Layer)   │
│                       │                             │
│                       ▼                             │
│  ┌─────────────────────────────────────────────┐   │
│  │        Multi-Armed Bandit Selection          │   │
│  │                                              │   │
│  │   ┌─────────┐  ┌─────────┐  ┌───────────┐  │   │
│  │   │  UCB1   │  │Thompson │  │  ε-Greedy │  │   │
│  │   │         │  │Sampling │  │ (baseline)│  │   │
│  │   └─────────┘  └─────────┘  └───────────┘  │   │
│  │                                              │   │
│  │   Reward = success / (duration + cost_pen)   │   │
│  └─────────────────────────────────────────────┘   │
│                       │                             │
│                       ▼                             │
│              [Selected Runner]                      │
└─────────────────────────────────────────────────────┘
```

### Neural-Symbolic Interface (#25) ✅ IMPLEMENTED

```python
from nsai import NeurosymbolicBandit

nsai = NeurosymbolicBandit.create_default()
runner, explanation = nsai.select_runner({
    "tags": ["docker-any"],
    "image": "python:3.11"
})

# explanation contains both symbolic and statistical reasoning
print(explanation)
```

```
┌─────────────────────────────────────────────────────┐
│            NEURAL-SYMBOLIC INTERFACE                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Symbolic → Neural:                                  │
│  ┌────────────────────────────────────────────┐     │
│  │ CSP filters feasible set → Dynamic action   │     │
│  │ space reduction for faster MAB convergence  │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  Neural → Symbolic:                                  │
│  ┌────────────────────────────────────────────┐     │
│  │ MAB statistics can be synced from deployed  │     │
│  │ Cloud Run service for warm-start            │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  Explanation:                                        │
│  ┌────────────────────────────────────────────┐     │
│  │ Both layers contribute to human-readable    │     │
│  │ explanation of runner selection decision    │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Consequences

### Positive

- **Garantierte Feasibility:** Symbolische Schicht eliminiert unmögliche Runner vor MAB-Auswahl
- **Schnellere Konvergenz:** MAB exploriert nur über gültige Runner (kleinerer Suchraum)
- **Explainability:** Ontologie ermöglicht Erklärungen ("Runner X gewählt wegen GPU-Support")
- **Paper-Material:** Neuartiger Ansatz für JKU AI Bachelor Thesis (#26)
- **Transferierbarkeit:** Architektur anwendbar auf andere Resource-Scheduling-Probleme

### Negative

- **Komplexität:** Zwei-Schichten-System erfordert mehr Wartung
- **Ontologie-Pflege:** Runner-Capabilities müssen manuell gepflegt werden
- **Cold-Start:** MAB braucht initiale Daten (mitigiert durch ε-Greedy Baseline)

### Neutral

- Runner-Tags bleiben als Fallback erhalten
- Bestehende CI/CD-Pipelines funktionieren unverändert

## Alternatives Considered

| Alternative | Pros | Cons | Why Not |
|-------------|------|------|---------|
| Pure MAB (nur #28) | Einfach, selbstlernend | Ignoriert Constraints, langsame Konvergenz | Feasibility nicht garantiert |
| Pure Rule-Based | Deterministisch, erklärbar | Keine Adaption, manuell | Lernt nicht aus Erfahrung |
| Deep RL (DQN/PPO) | State-of-the-art | Overengineered, Sample-ineffizient | Für <10 Runner übertrieben |
| Contextual Bandits | Nutzt Job-Features | Noch keine Constraints | Phase 5 möglich |

## Implementation

### Phase 1: MAB Baseline (Issue #28) ✅ COMPLETE
- [x] UCB1, Thompson Sampling, ε-Greedy
- [x] FastAPI Webhook Handler
- [x] State Persistence
- [x] Deploy to GCP Cloud Run
- [x] Webhook integration (collecting data)

**Service:** https://runner-bandit-m5cziijwqa-lz.a.run.app  
**Stats:** 50 observations, 96% success rate (as of 2026-02-05)

### Phase 2: Symbolic Layer (Issues #22-24) ✅ COMPLETE
- [x] #22: Runner Capability Ontology
- [x] #23: Job Requirement Parser
- [x] #24: Constraint Satisfaction Module

**Location:** `services/nsai/` (ontology, parser, csp)

### Phase 3: Integration (Issue #25) ✅ COMPLETE
- [x] #25: Neural-Symbolic Interface (`NeurosymbolicBandit` class)
- [x] Explanation generation for both layers
- [x] MAB service sync capability
- [ ] A/B Testing: Pure MAB vs. Neurosymbolic (pending)
- [ ] Performance Comparison (pending)

**MR:** !12 (feature/25-nsai-interface)

### Phase 4: Documentation (Issue #26) 🔄 IN PROGRESS
- [ ] #26: JKU Bachelor Paper Draft
- [ ] Evaluation & Results
- [x] README with usage examples
- [x] ADR updates

### Phase 5: Advanced Features (Future)
- [ ] Contextual Bandits (job features as context)
- [ ] Online learning integration
- [ ] GitLab Pages dashboard for stats

## Related

### Internal
- Epic: ops/backoffice#27 [EPIC] Neurosymbolic AI Runner Selection
- ops/backoffice#28 [MAB] Runner Bandit Service - Baseline ✅
- ops/backoffice#22 [NSAI] Runner Capability Ontology Design ✅
- ops/backoffice#23 [NSAI] Job Requirement Parser ✅
- ops/backoffice#24 [NSAI] Constraint Satisfaction Module ✅
- ops/backoffice#25 [NSAI] Neural-Symbolic Interface ✅
- ops/backoffice#26 [NSAI] JKU Bachelor Paper Draft 🔄

### Literature
- Garcez, A. et al. (2019). Neural-Symbolic Computing: An Effective Methodology for Principled Integration of Machine Learning and Reasoning
- Lattimore, T. & Szepesvári, C. (2020). Bandit Algorithms. Cambridge University Press.
- d'Avila Garcez, A. & Lamb, L. (2020). Neurosymbolic AI: The 3rd Wave

### External
- [OWL Web Ontology Language](https://www.w3.org/OWL/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
