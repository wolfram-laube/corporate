# GOV-003: Publication Workflow — Quarto as Source of Truth

**Status:** Accepted
**Date:** 2026-02-07
**Author:** Wolfram Laube
**Tags:** documentation, publishing, quarto, latex, governance
**Supersedes:** —
**Superseded by:** —

## Context

Blauweiss LLC produces multiple documentation types: academic papers
(NSAI, CLARISSA), internal reports, technical documentation, and
experiment notebooks. These documents share common requirements:

- Reproducible figure generation from code
- Multi-format output (PDF for submission, HTML for review/sharing)
- Bibliography management
- Cross-referencing between sections, figures, and tables
- Version control of source files

The NSAI paper (v0.3.0) was initially authored in pure LaTeX (925 lines),
with a separate Jupyter notebook generating figures. This created a
*two-repo, manual-copy problem*: figures generated in backoffice had to
be manually transferred to the paper source, breaking the single-source
principle.

GOV-002 established Jupyter Notebook standards. This ADR extends the
publication pipeline to cover the full authoring workflow.

## Decision

### Quarto (.qmd) as Source of Truth

All publications MUST use Quarto Markdown (.qmd) as the primary source
format. LaTeX is used only for elements with no Markdown equivalent:

| Element | Format | Example |
|---------|--------|---------|
| Text, headings, lists | Markdown | `## Section`, `- item` |
| Math (inline/display) | LaTeX in Markdown | `$x^2$`, `$$ R_T = ... $$` |
| Cross-references | Quarto native | `@sec-intro`, `@fig-reward`, `@tbl-results` |
| Bibliography | Quarto citeproc | `[@auer2002finite]`, `references.bib` |
| Figures from code | Python code cells | `` ```{python}``  with `#| label: fig-*` |
| Static figures | Markdown images | `![caption](figures/fig.pdf)` |
| Tables (simple) | Markdown tables | Pipe tables with `: {#tbl-*}` |
| Algorithm environments | Raw LaTeX block | `` ```{=latex} `` |
| Theorem/Definition | Quarto divs | `::: {#def-regret}` |
| Custom LaTeX commands | YAML header-includes | `\newcommand{\nsai}{...}` |

### Project Structure

```
backoffice/docs/publications/<paper-slug>/
├── _quarto.yml          # Project config: render order, shared settings
├── experiment.qmd       # Computational notebook (generates figures)
├── paper.qmd            # Paper text (Markdown + LaTeX passthrough)
├── references.bib       # Bibliography
├── figures/             # Static figures (architecture diagrams, etc.)
│   └── .gitkeep
├── _output/             # Generated (gitignored)
│   ├── paper.pdf
│   ├── paper.html
│   └── experiment.html
└── _freeze/             # Cached execution results (committed)
```

### Build Flow

```
quarto render
  → experiment.qmd executes Python → figures/*.pdf
  → paper.qmd includes figures → _output/paper.pdf + paper.html
```

Single command, deterministic output. The `_freeze/` directory caches
execution results so rebuilds are fast when only text changes.

### _quarto.yml Template

```yaml
project:
  type: default
  output-dir: _output
  render:
    - experiment.qmd    # Runs first → generates figures
    - paper.qmd         # Paper picks up figures

bibliography: references.bib
number-sections: true

format:
  pdf:
    documentclass: article
    classoption: [11pt, a4paper]
    geometry: margin=2.5cm
    colorlinks: true
  html:
    theme: darkly
    code-fold: true
    self-contained: true
```

### Where Publications Live

| Content Type | Location | Rationale |
|-------------|----------|-----------|
| Paper source + experiment | `backoffice/docs/publications/<slug>/` | Near the code that generates figures |
| Final PDF (release artifact) | `corporate/docs/publications/` | Firm's "vitrine" for stakeholders |
| CLARISSA-specific research | `clarissa/docs/publications/` | Domain-specific, separate CI |

### CI Pipeline Integration

```yaml
# In backoffice/.gitlab-ci.yml
publication:build:
  stage: docs
  image: quarto/quarto:latest  # Or custom image with Python + deps
  script:
    - cd docs/publications/nsai-runner-selection-2026
    - pip install matplotlib numpy
    - quarto render
  artifacts:
    paths:
      - docs/publications/nsai-runner-selection-2026/_output/
  rules:
    - changes:
        - docs/publications/nsai-runner-selection-2026/**
```

## Rationale

### Why Quarto over pure LaTeX?

1. **Markdown is readable** — 697 lines vs 925 lines for the same paper,
   with far less syntactic noise.
2. **Code-figure integration** — Python cells generate figures inline;
   no manual copy step.
3. **Multi-format output** — PDF + HTML from one source, with interactive
   elements in HTML.
4. **Lower barrier** — Team members (Ian, Mike) can contribute without
   deep LaTeX knowledge.
5. **LaTeX when needed** — Raw LaTeX blocks (`{=latex}`) preserve
   algorithm environments and custom commands.

### Why not pure Markdown / Pandoc?

Quarto IS Pandoc (plus Jupyter integration, freeze caching, native
cross-references, and theorem environments). Using Quarto over raw
Pandoc gives us the project system (`_quarto.yml`) and reproducible
execution for free.

### Why freeze?

The `_freeze/` directory stores execution results so that:
- `quarto render` is fast when only text changes (no re-execution)
- CI doesn't need the full Python environment for text-only edits
- Results are reproducible across machines (committed to Git)

## Consequences

- All new publications follow this structure
- Existing NSAI LaTeX paper remains as-is (v3 is final for Q1 2026)
- NSAI Quarto version serves as reference implementation
- GOV-002 notebook standards apply to `experiment.qmd` files
- `_freeze/` directories are committed to Git
- `_output/` directories are gitignored

## References

- GOV-002: Jupyter Notebook Documentation Standards
- Quarto documentation: https://quarto.org/docs/authoring/
- NSAI paper: `backoffice/docs/publications/nsai-runner-selection-2026/`
