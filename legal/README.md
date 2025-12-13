# Legal

Gründungsdokumente, Verträge und rechtliche Vorlagen.

## Struktur

```
legal/
├── formation/      # Gründungsdokumente (APOR, Operating Agreement, etc.)
│   ├── src/        # Quelldateien (MD, LaTeX)
│   ├── dist/       # Generierte Artefakte (PDF, DOCX)
│   └── signed/     # → Google Drive
└── templates/      # Wiederverwendbare Vorlagen
```

## Gründungsdokumente

| Nr. | Dokument | DE | EN | Status |
|-----|----------|----|----|--------|
| 01 | APOR-Antrag | ✅ | ✅ | Erstellt |
| 02 | Operating Agreement | ✅ | ✅ | Unterschrift ausstehend |
| 03 | Contractor Agreement | ✅ | ✅ | APOR-Genehmigung ausstehend |

## Formate

Jedes Dokument existiert in mehreren Formaten:

| Format | Zweck |
|--------|-------|
| `.md` | Quelle, versionierbar, Diffs |
| `.tex` | LaTeX für hochwertigen Druck |
| `.docx` | Für Word-Bearbeitung, Unterschriften |
| `.pdf` | Finale Version, unveränderbar |
| `.html` | Web-Ansicht |

## Signierte Dokumente

📁 **[Google Drive → Legal/Signed](https://drive.google.com/...)**
