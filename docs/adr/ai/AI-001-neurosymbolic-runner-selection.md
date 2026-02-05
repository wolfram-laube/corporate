# AI-001: Neurosymbolic Runner Selection Architecture

**Status:** Accepted  
**Date:** 2026-02-04  
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

### Neural-Symbolic Interface (#25)

```
┌─────────────────────────────────────────────────────┐
│            NEURAL-SYMBOLIC INTERFACE                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Symbolic → Neural:                                  │
│  ┌────────────────────────────────────────────┐     │
│  │ Constraint violations → Negative reward     │     │
│  │ Ontology features → Bandit context vectors  │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  Neural → Symbolic:                                  │
│  ┌────────────────────────────────────────────┐     │
│  │ Learned preferences → Ontology annotations  │     │
│  │ Performance data → Knowledge Graph updates  │     │
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
| Contextual Bandits | Nutzt Job-Features | Noch keine Constraints | Phase 2 möglich |

## Implementation

### Phase 1: MAB Baseline (Issue #28) ✅
- [x] UCB1, Thompson Sampling, ε-Greedy
- [x] FastAPI Webhook Handler
- [x] State Persistence
- [ ] Deploy to GCP Cloud Run (in progress)
- [ ] Collect baseline data (2 weeks)

### Phase 2: Symbolic Layer (Issues #22-24)
- [ ] #22: Runner Capability Ontology (OWL/RDF)
- [ ] #23: Job Requirement Parser
- [ ] #24: Constraint Satisfaction Module

### Phase 3: Integration (Issue #25)
- [ ] #25: Neural-Symbolic Interface
- [ ] A/B Testing: Pure MAB vs. Neurosymbolic
- [ ] Performance Comparison Paper

### Phase 4: Documentation (Issue #26)
- [ ] #26: JKU Bachelor Paper Draft
- [ ] Evaluation & Results

## Related

### Internal
- Epic: ops/backoffice#27 [EPIC] Neurosymbolic AI Runner Selection
- ops/backoffice#28 [MAB] Runner Bandit Service - Baseline
- ops/backoffice#22 [NSAI] Runner Capability Ontology Design
- ops/backoffice#23 [NSAI] Job Requirement Parser
- ops/backoffice#24 [NSAI] Constraint Satisfaction Module
- ops/backoffice#25 [NSAI] Neural-Symbolic Interface
- ops/backoffice#26 [NSAI] JKU Bachelor Paper Draft

### Literature
- Garcez, A. et al. (2019). Neural-Symbolic Computing: An Effective Methodology for Principled Integration of Machine Learning and Reasoning
- Lattimore, T. & Szepesvári, C. (2020). Bandit Algorithms. Cambridge University Press.
- d'Avila Garcez, A. & Lamb, L. (2020). Neurosymbolic AI: The 3rd Wave

### External
- [OWL Web Ontology Language](https://www.w3.org/OWL/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
