# GOV-002: Jupyter Notebook Documentation Standards

**Status:** Accepted  
**Date:** 2026-02-05  
**Author:** Wolfram Laube  
**Tags:** documentation, jupyter, standards, governance  
**Supersedes:** —  
**Superseded by:** —

## Context

Jupyter Notebooks sind zentrale Dokumentations- und Demo-Artefakte für unsere AI/ML-Komponenten. Ohne klare Standards entstehen inkonsistente, schwer wartbare Notebooks die:

- Keinen klaren Einstiegspunkt bieten
- Setup-Schritte nicht dokumentieren
- Keine API-Referenz enthalten
- Nicht mit dem Code synchron bleiben

Die kürzliche Überarbeitung des NSAI demo.ipynb hat gezeigt, dass ein strukturierter Ansatz die Qualität erheblich verbessert.

## Decision

Alle Jupyter Notebooks in blauweiss_llc MÜSSEN folgende Struktur einhalten:

### Pflicht-Abschnitte

```
1. 🧠 Title & Overview
   - Projektname mit Emoji
   - Version Badge
   - 1-2 Sätze Beschreibung
   - Quick Links (README, ADR, Service URLs)

2. 🔧 Setup
   - Colab Setup (falls relevant)
   - pip install Befehle
   - Import Statements
   - Umgebungsvariablen

3. 🚀 Quick Start
   - Minimales funktionierendes Beispiel
   - Copy-paste ready
   - Erwarteter Output als Kommentar

4. 📚 Deep Dive (optional)
   - Detaillierte Erklärungen
   - Komponenten einzeln
   - Visualisierungen

5. 📊 API Reference
   - Tabelle mit Methoden/Parametern
   - Return Types
   - Beispiele

6. 🔗 Related
   - Links zu Docs
   - Issues/Epics
   - Externe Ressourcen
```

### Pflicht-Metadaten

Jedes Notebook MUSS in der ersten Markdown-Zelle enthalten:

```markdown
# 🧠 [Projekt] - [Kurzbeschreibung]

> **Version X.Y.Z** - [Changelog Highlight]

[1-2 Sätze was das Notebook zeigt]

**Quick Links:**
- [README](../README.md)
- [ADR](link-to-adr)
- [Service](https://...)
```

### Code-Zellen Standards

1. **Erste Code-Zelle:** Immer Setup/Imports
2. **Output:** Erwarteter Output als Kommentar oder Markdown
3. **Error Handling:** Try/Except für externe Services
4. **Idempotenz:** Zellen sollten mehrfach ausführbar sein

### Qualitätskriterien

| Kriterium | Pflicht | Beschreibung |
|-----------|---------|--------------|
| Ausführbar | ✅ | Notebook läuft von oben nach unten ohne Fehler |
| Aktuell | ✅ | API-Beispiele matchen aktuelle Code-Version |
| Selbsterklärend | ✅ | Keine externen Docs nötig für Quick Start |
| Colab-kompatibel | ⚠️ | Falls GitHub Mirror existiert |
| Visualisierungen | ⚠️ | Wo sinnvoll (Plots, Diagramme) |

### Review Checklist

Bei jedem MR der Notebooks berührt:

- [ ] Title Cell mit Version aktualisiert?
- [ ] Quick Start funktioniert standalone?
- [ ] API Reference vollständig?
- [ ] Alle Zellen ausführbar (Kernel → Restart & Run All)?
- [ ] Links aktuell?
- [ ] Keine hardcoded Secrets/Tokens?

## Consequences

### Positive

- **Konsistenz:** Alle Notebooks haben gleiche Struktur
- **Onboarding:** Neue Teammitglieder finden sich sofort zurecht
- **Wartbarkeit:** Klare Stellen für Updates bei API-Änderungen
- **Colab-Ready:** GitHub Mirror ermöglicht direkte Colab-Nutzung

### Negative

- **Overhead:** Initiale Erstellung dauert länger
- **Pflege:** Version Bumps müssen synchron gehalten werden

### Neutral

- Bestehende Notebooks müssen migriert werden (siehe Implementation)

## Implementation

### Phase 1: Template erstellen
- [ ] `docs/templates/notebook-template.ipynb` in corporate
- [ ] Pre-commit Hook für Notebook Linting (optional)

### Phase 2: Migration
- [ ] `services/nsai/notebooks/demo.ipynb` ✅ (bereits konform)
- [ ] `experimental/jupyter/test-notebook.ipynb` → evaluieren/löschen
- [ ] Zukünftige Notebooks nach Template

### Phase 3: Automation (Future)
- [ ] CI Job: Notebook Execution Test
- [ ] Auto-sync Version aus pyproject.toml

## Template

Siehe: [`docs/templates/notebook-template.ipynb`](../templates/notebook-template.ipynb)

## Related

### Internal
- [GOV-001: ADR Structure](./GOV-001-adr-structure.md)
- [NSAI Demo Notebook](https://gitlab.com/wolfram_laube/blauweiss_llc/ops/backoffice/-/blob/main/services/nsai/notebooks/demo.ipynb) (Reference Implementation)

### External
- [Google Colab Best Practices](https://colab.research.google.com/)
- [Jupyter Notebook Best Practices](https://jupyter-notebook.readthedocs.io/)
