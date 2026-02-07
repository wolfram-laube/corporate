# GOV-003: Publication Pipeline Architecture

**Status:** Proposed  
**Date:** 2026-02-07  
**Author:** Wolfram Laube  
**Tags:** governance, documentation, publishing, quarto, latex, jupyter  
**Supersedes:** —  
**Superseded by:** —

## Context

Blauweiss produziert zunehmend technische Dokumentation, die über reine Code-Docs hinausgeht:

| Dokument | Format heute | Problem |
|----------|-------------|---------|
| NSAI Bachelor Paper | `.tex` + manuell kopierte Zahlen | Experiment-Daten nicht reproduzierbar im Paper |
| NSAI Experiment | `.ipynb` (Jupyter) | Generiert Plots, aber kein Link zum Paper-Build |
| NSAI Dashboard | `.html` (standalone) | Separat erstellt, driftet vom Paper ab |
| CI-Metrics Report | geplant | Noch keine Pipeline |
| CLARISSA Publications | `ijacsa-2026/`, `spe-europe-2026/` | Eigenes Silo in CLARISSA |

### Das Kernproblem

Ein Experiment-Ergebnis durchläuft heute **drei manuelle Übergaben**:

```
Notebook (experiment.ipynb)
    ↓  plt.savefig('fig2.pdf')      ← manuell
Figures (figures/fig2.pdf)
    ↓  \includegraphics{fig2.pdf}   ← manuell  
Paper (nsai_paper.tex)
    ↓  pdflatex                     ← manuell
PDF (nsai_paper.pdf)
```

Bei jeder Änderung am Experiment müssen Zahlen im Paper händisch aktualisiert werden.
Tabellen, Plots und Prose können auseinanderlaufen. Das ist fehleranfällig und
widerspricht dem Prinzip einer Single Source of Truth.

### Zusätzliche Anforderungen

1. **JKU-Einreichung:** Die Bachelor-Thesis muss als LaTeX-PDF eingereicht werden (JKU-Template)
2. **Colab-Kompatibilität:** Notebooks müssen in Google Colab ausführbar bleiben
3. **Experimentierfreiheit:** Forschung braucht Scratch-Notebooks ohne Publikationszwang
4. **Multi-Output:** Dasselbe Ergebnis soll als PDF (akademisch), HTML (interaktiv) und Slides (Präsentation) verfügbar sein

---

## Dialektische Analyse

### These: LaTeX als Source of Truth

> *„Das Paper ist ein `.tex`-File. Alles andere ist Zuarbeit."*

**Das traditionelle akademische Modell.** Der Autor schreibt LaTeX, kontrolliert
jedes Detail — Formeln, Float-Placement, Mikrotypografie. Experiment-Ergebnisse
werden als Zahlen eingetippt, Plots als fertige PDFs eingebunden.

#### Stärken

- **Volle Kontrolle:** LaTeX bietet präzise typografische Steuerung
- **Akademischer Standard:** Jede Uni, jede Konferenz akzeptiert `.tex`
- **Bewährt:** 40+ Jahre Ökosystem, stabil, gut dokumentiert
- **JKU-kompatibel:** Template-Klassen, `\maketitle`, Eidesstattliche Erklärung — alles nativ
- **Kein Build-Overhead:** `pdflatex` + `bibtex` reicht, keine weitere Toolchain

#### Schwächen

- **Keine Reproduzierbarkeit:** Zahlen im Paper sind Copy-Paste aus dem Notebook — Fehlerquelle
- **Kein Rückkanal:** Wenn sich Experiment-Daten ändern, merkt das Paper es nicht
- **Single Output:** LaTeX → PDF. HTML oder Slides brauchen separate Arbeit
- **Prose/Code-Trennung:** Der Leser sieht Ergebnisse, aber nicht den Code der sie erzeugt
- **Hohe Einstiegshürde:** LaTeX-Syntax ist für Nicht-Eingeweihte schwer lesbar

### Antithese: Notebook als Source of Truth

> *„Das Notebook IST das Paper. Code, Text, Ergebnisse — ein Dokument."*

**Das Literate-Programming-Ideal** (Knuth, 1984). Ein Jupyter Notebook enthält
Prosa, Code und Output zusammen. Was ausgeführt wird, IST das Ergebnis.
Keine manuelle Übergabe, keine Drift.

#### Stärken

- **Reproduzierbar:** `Kernel → Restart & Run All` generiert alle Ergebnisse neu
- **Code = Beweis:** Der Leser sieht exakt, wie eine Zahl berechnet wurde
- **Colab-kompatibel:** `.ipynb` öffnet direkt in Google Colab
- **Interaktiv:** Leser können Parameter ändern und Ergebnisse live sehen
- **Niedrige Einstiegshürde:** Markdown + Python, kein LaTeX nötig

#### Schwächen

- **Keine akademische Akzeptanz:** Man kann kein `.ipynb` bei der JKU einreichen
- **Markdown-Limits:** Keine Theorem-Environments, kein `\Cref{}`, kein Algorithm-Pseudocode
- **Linearitätszwang:** Ein Notebook ist eine Sequenz — akademische Papers sind es nicht
- **Format-Lock:** JSON-basiert, grauenhafte Git-Diffs, fragiles Format
- **Experimentierfreiheit leidet:** Wenn das Notebook = Publikation, wird jede Zelle zur Last

### Synthese: Drei-Ebenen-Pipeline mit Quarto als Brücke

> *„Jede Ebene hat ihre eigene Source of Truth. Quarto verbindet sie."*

**Die Erkenntnis:** Es sind nicht zwei, sondern **drei verschiedene Artefakte**
mit verschiedenem Lifecycle, verschiedenem Publikum und verschiedenem Format.
Die Lösung ist nicht „eines ersetzt die anderen", sondern eine Pipeline,
in der jede Ebene ihre Stärke ausspielt:

```
┌─────────────────────────────────────────────────────────────┐
│  Ebene 3: THESIS                                            │
│  Format: .tex (JKU-Template)     Publikum: Prüfungsamt     │
│  Source of Truth: thesis.tex                                 │
│  Enthält: Formale Rahmung, Einleitung, Methodik, Reflexion  │
│  Bindet ein: Paper (Ebene 2) als Kern-Kapitel               │
│  Build: pdflatex + bibtex                                    │
├─────────────────────────────────────────────────────────────┤
│  Ebene 2: PAPER                                             │
│  Format: .tex + .bib             Publikum: Akademisch       │
│  Source of Truth: nsai_paper.tex                             │
│  Enthält: Algorithmen, Propositionen, Diskussion             │
│  Bezieht: Figures + Zahlen aus Ebene 1                      │
│  Build: pdflatex + bibtex                                    │
├─────────────────────────────────────────────────────────────┤
│  Ebene 1: EXPERIMENT                                        │
│  Format: .ipynb (Jupyter)        Publikum: Technisch        │
│  Source of Truth: experiment.ipynb                            │
│  Enthält: Code, Assertions, Plots                            │
│  Generiert: figures/*.pdf + results.json                     │
│  Build: quarto render ODER jupyter nbconvert --execute       │
└─────────────────────────────────────────────────────────────┘
```

**Quarto** sitzt an der Schnittstelle zwischen Ebene 1 und 2. Es:

- Führt das Notebook aus (`quarto render experiment.ipynb`)
- Extrahiert Figures als PDF/PNG
- Kann optional eine HTML-Version mit interaktiven Charts generieren
- Ersetzt aber NICHT den LaTeX-Kern der Ebenen 2 und 3

**Der Build-Graph:**

```
Scratch Notebooks (Colab, frei, ephemer)
    ↓ Erkenntnisse reifen, Ansatz steht fest
Publication Notebook (.ipynb, CI-getestet, versioniert)
    ↓ quarto render / nbconvert --execute
    ├── figures/*.pdf
    ├── results.json (optional: maschinenlesbare Ergebnisse)
    └── dashboard.html (interaktive Version)
           ↓ \includegraphics{figures/fig2.pdf}
Paper (.tex + .bib)
    ↓ \input{chapters/nsai-paper}
Thesis (.tex + JKU-Template)
    ↓ pdflatex → bibtex → pdflatex → pdflatex
Eingereicht bei JKU ✓
```

---

## Decision

### 1. Drei Artefakt-Typen mit klaren Verantwortlichkeiten

| Ebene | Artefakt | Format | Source of Truth | Build-Tool |
|-------|----------|--------|-----------------|------------|
| 1 | Experiment | `.ipynb` | Notebook | Quarto / nbconvert |
| 2 | Paper | `.tex` + `.bib` | LaTeX-File | pdflatex + bibtex |
| 3 | Thesis | `.tex` + JKU-Klasse | LaTeX-File | pdflatex + bibtex |

### 2. Zwei Notebook-Phasen

| Phase | Scratch Notebook | Publication Notebook |
|-------|-----------------|---------------------|
| **Zweck** | Erkenntnisgewinn | Ergebnisnachweis |
| **Wo** | Colab, Feature-Branch, CLARISSA | backoffice/main, CI-getestet |
| **Disziplin** | Keine — Chaos erwünscht | Reproduzierbar, linear, assertiert |
| **Git** | Branch, kann weg | Main, versioniert, tagged |
| **Quarto** | Nein | Ja — rendert Figures + optional HTML |
| **GOV-002** | Empfohlen | Pflicht |

### 3. Verzeichnisstruktur

```
backoffice/
├── services/nsai/
│   ├── __init__.py, interface.py, ...     ← Code
│   └── notebooks/
│       ├── nsai_experiment.ipynb           ← Publication Notebook (Ebene 1)
│       └── _quarto.yml                    ← Render-Config
│
└── docs/publications/
    └── nsai-runner-selection-2026/
        ├── nsai_paper.tex                  ← Paper (Ebene 2)
        ├── nsai_paper.bib
        ├── figures/                        ← Generated by Notebook, .gitignored
        │   ├── fig2_cumulative_reward.pdf
        │   └── ...
        ├── nsai_results.html               ← Interactive Dashboard
        └── Makefile                        ← Orchestriert den Build
```

Für die Thesis (Ebene 3), wenn es soweit ist:

```
backoffice/docs/thesis/
├── thesis.tex                              ← Hauptdokument
├── jku-template.cls                        ← JKU-Formatvorlage
├── chapters/
│   ├── 01-introduction.tex
│   ├── 02-background.tex
│   ├── 03-nsai-paper.tex                   ← \input{} oder Kopie von Ebene 2
│   ├── 04-discussion.tex
│   └── 05-conclusion.tex
├── frontmatter/
│   ├── titlepage.tex
│   ├── abstract.tex
│   └── declaration.tex                     ← Eidesstattliche Erklärung
└── references.bib
```

### 4. CI Pipeline

```yaml
paper:build:
  stage: docs
  rules:
    - changes:
        - services/nsai/notebooks/**
        - docs/publications/nsai-*/**
  script:
    # Ebene 1: Notebook ausführen, Figures generieren
    - cd services/nsai/notebooks
    - quarto render nsai_experiment.ipynb --to pdf  # oder nbconvert
    - cp figures/*.pdf ../../../docs/publications/nsai-runner-selection-2026/figures/
    
    # Ebene 2: Paper kompilieren
    - cd ../../../docs/publications/nsai-runner-selection-2026
    - pdflatex nsai_paper && bibtex nsai_paper && pdflatex nsai_paper && pdflatex nsai_paper
  artifacts:
    paths:
      - docs/publications/nsai-runner-selection-2026/nsai_paper.pdf
      - docs/publications/nsai-runner-selection-2026/nsai_results.html
```

### 5. Colab-Kompatibilität

Das Publication Notebook bleibt ein Standard-`.ipynb`. Quarto-spezifische
Annotations in Markdown-Cells (z.B. `#| label: fig-reward`) werden von
Colab einfach als Text gerendert — sie stören nicht.

Der GitHub-Mirror (via bestehende Pipeline) stellt sicher, dass der
"Open in Colab"-Button funktioniert.

---

## Consequences

### Positive

- **Reproduzierbar:** Ein `git push` generiert Paper-PDF mit aktuellen Experiment-Daten
- **Single Source of Truth:** Jede Ebene hat genau eine, klar definierte
- **Colab bleibt:** Notebooks sind Standard-Jupyter, keine Lock-in
- **Experimentierfreiheit:** Scratch-Notebooks leben in Branches, ohne Publikationsdruck
- **Multi-Output:** Notebook → Figures + HTML; Paper → PDF; Thesis → PDF
- **CI-verifiziert:** Notebook-Assertions sichern Datenintegrität

### Negative

- **Toolchain-Komplexität:** Quarto muss im CI-Image installiert sein
- **Zwei Notebook-Phasen:** Muss kommuniziert werden (Scratch vs. Publication)
- **LaTeX bleibt Pflicht:** Für Paper und Thesis wird LaTeX-Kompetenz benötigt
- **Figure-Pfad-Disziplin:** Notebook muss in den richtigen Ordner schreiben

### Neutral

- Quarto ist optional für Ebene 1 — `nbconvert --execute` tut's auch
- Bestehende CLARISSA-Publications bleiben in CLARISSA (anderes Fachgebiet)
- Corporate bekommt nur fertige PDFs (Release-Artifacts), keinen Source-Code

---

## Alternatives Considered

| Alternative | Stärken | Schwächen | Warum nicht |
|-------------|---------|-----------|-------------|
| **Alles in LaTeX** (Status quo) | Einfach, bewährt | Zahlen-Drift, kein Multi-Output | Fehleranfällig bei Updates |
| **Alles in Notebook** (.ipynb → PDF) | Voll reproduzierbar | Kein JKU-Einreichformat, keine Theorem-Envs | Akademisch nicht akzeptabel |
| **Quarto als einzige Source** (.qmd) | Eleganteste Lösung | Kein Colab, neues Format, JKU-Template-Aufwand | Lock-in, Kill the Notebook |
| **Overleaf + manueller Upload** | Kollaborativ | Kein CI, manuelle Syncs | Nicht automatisierbar |
| **Pandoc Markdown → LaTeX** | Einfacher Source | LaTeX-Features fehlen (Algorithmen, Theoreme) | Zu limitiert für akademische Papers |

---

## Implementation

### Phase 1: Sofort (NSAI v0.3.0 Paper)

- [x] Paper als `.tex` + `.bib` (erledigt)
- [x] Experiment-Notebook mit `plt.savefig()` (erledigt)
- [x] Interaktive HTML-Version (erledigt)
- [ ] `Makefile` das den Build orchestriert
- [ ] Verzeichnisstruktur in backoffice anlegen
- [ ] Files committen (Paper, Notebook v2, Figures)

### Phase 2: CI-Integration

- [ ] Quarto im CI-Image installieren (oder nbconvert als Fallback)
- [ ] `paper:build` Job in `.gitlab-ci.yml`
- [ ] Figure-Generation automatisieren
- [ ] Artifact-Upload für fertige PDFs

### Phase 3: Thesis-Vorbereitung (Q1 2026)

- [ ] JKU-Template beschaffen / erstellen
- [ ] Thesis-Struktur anlegen (`docs/thesis/`)
- [ ] Paper als Chapter einbinden
- [ ] Formale Elemente (Titelblatt, Erklärung, Abstract)

### Phase 4: Erweiterung (Future)

- [ ] CI-Metrics Paper (gleiche Pipeline)
- [ ] Quarto-HTML als GitLab Pages publizieren
- [ ] Template für neue Publikationen (`docs/templates/publication-template/`)

---

## Zusammenfassung

```
                ┌─────────────┐
                │   Thesis    │  ← Ebene 3: JKU-LaTeX
                │  (.tex+cls) │     Formale Einreichung
                └──────┬──────┘
                       │ \input{}
                ┌──────┴──────┐
                │    Paper    │  ← Ebene 2: LaTeX
                │ (.tex+.bib) │     Akademischer Kern
                └──────┬──────┘
                       │ \includegraphics{}
                ┌──────┴──────┐
                │  Notebook   │  ← Ebene 1: Jupyter
                │   (.ipynb)  │     Reproduzierbare Ergebnisse
                └──────┬──────┘
                       │ quarto render
                ┌──────┴──────┐
                │   Figures   │  ← Generierte Artefakte
                │  + HTML     │     .pdf, .png, .html
                └─────────────┘

    Colab ←→ Notebook ←→ CI Pipeline ←→ Paper ←→ JKU
```

**Kernaussage:** Jede Ebene bleibt in ihrem natürlichen Format.
Quarto verbindet, ohne zu ersetzen.

---

## Related

### Internal

- [GOV-001: ADR Structure](../governance/GOV-001-adr-structure.md) — Wo ADRs leben
- [GOV-002: Notebook Standards](../governance/GOV-002-notebook-standards.md) — Wie Notebooks strukturiert sind
- [AI-001: Neurosymbolic Runner Selection](../ai/AI-001-neurosymbolic-runner-selection.md) — Erster Anwendungsfall
- NSAI Paper: `backoffice/docs/publications/nsai-runner-selection-2026/`
- NSAI Experiment: `backoffice/services/nsai/notebooks/nsai_experiment.ipynb`

### External

- [Quarto: Getting Started](https://quarto.org/docs/get-started/)
- [Quarto: Using Jupyter Notebooks](https://quarto.org/docs/tools/jupyter-lab.html)
- [Knuth, D. (1984): Literate Programming](https://doi.org/10.1093/comjnl/27.2.97)
- [JKU Thesis Guidelines](https://www.jku.at/studium/studienorganisation/abschlussarbeiten/)
