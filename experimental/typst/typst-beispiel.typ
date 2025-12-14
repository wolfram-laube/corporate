// =============================================================================
// BLAUWEISS-EDV LLC – Typst Beispiel-Dokument
// =============================================================================
// Kompilieren mit: typst compile typst-beispiel.typ typst-beispiel.pdf
// Live-Preview: typst watch typst-beispiel.typ
// =============================================================================

// Seiteneinstellungen
#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 2.5cm),
  header: [
    #set text(9pt, fill: gray)
    BLAUWEISS-EDV LLC #h(1fr) Beispiel-Dokument
  ],
  footer: context [
    #set text(9pt, fill: gray)
    #h(1fr) Seite #counter(page).display() #h(1fr)
  ]
)

// Schriftarten
#set text(size: 11pt, lang: "de")
#set heading(numbering: "1.1")

// Farben (Corporate Design)
#let blau = rgb("#0066cc")
#let grau = rgb("#666666")

// =============================================================================
// Dokument
// =============================================================================

#align(center)[
  #text(24pt, weight: "bold", fill: blau)[BLAUWEISS-EDV LLC]
  
  #v(0.5cm)
  
  #text(14pt)[_Beispiel-Dokument für Typst_]
  
  #v(0.3cm)
  
  #text(10pt, fill: grau)[Erstellt: #datetime.today().display()]
]

#v(1cm)

= Einführung

Dieses Dokument zeigt die Möglichkeiten von *Typst* als Alternative zu LaTeX und Markdown.

== Vorteile von Typst

- *Einfache Syntax* – fast wie Markdown
- *Schnelle Kompilierung* – Millisekunden statt Minuten
- *Eingebautes Scripting* – für komplexe Layouts
- *Moderne Features* – entwickelt für 2024+

== Textformatierung

Hier ist *fetter Text*, _kursiver Text_, und `Code`.

Man kann auch #text(fill: blau)[farbigen Text] verwenden.

= Tabellen

#table(
  columns: (auto, 1fr, 1fr),
  inset: 10pt,
  align: horizon,
  table.header(
    [*Position*], [*Beschreibung*], [*Betrag*],
  ),
  [1], [Beratungsleistung Remote], [EUR 8.400,00],
  [2], [Beratungsleistung On-Site], [EUR 1.200,00],
  [], [*Gesamt*], [*EUR 9.600,00*],
)

= Code-Beispiele

```python
def hello_world():
    print("Hello from BLAUWEISS-EDV LLC!")
    return 42
```

= Mathematik

Typst kann auch Formeln:

$ E = m c^2 $

Oder komplexer:

$ integral_0^infinity e^(-x^2) dif x = sqrt(pi) / 2 $

= Bilder einbinden

// Bild einbinden (wenn vorhanden):
// #image("logo.png", width: 30%)

#rect(
  width: 100%,
  height: 3cm,
  fill: luma(240),
  stroke: grau,
)[
  #align(center + horizon)[
    _Hier könnte ein Logo sein_
    
    `#image("logo.png", width: 30%)`
  ]
]

= Fazit

Typst ist eine moderne Alternative für:

+ *Einfache Dokumente* – schneller als LaTeX
+ *Komplexe Layouts* – mächtiger als Markdown  
+ *Automatisierung* – perfekt für CI/CD Pipelines

#v(1cm)

#line(length: 100%, stroke: grau)

#align(center)[
  #text(9pt, fill: grau)[
    BLAUWEISS-EDV LLC | Texas, USA | info\@blauweiss-edv.com
  ]
]
