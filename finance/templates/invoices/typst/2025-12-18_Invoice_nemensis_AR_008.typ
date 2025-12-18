// =============================================================================
// BLAUWEISS-EDV LLC – Rechnung AR_008
// Generiert am 2025-12-18 23:23
// =============================================================================

// === RECHNUNGSDATEN ===
#let rechnung_nr = "AR_008"
#let datum = "18. Dezember 2025"
#let projekt_nr = "00003151"

// Kunde
#let kunde_name = "nemensis AG Deutschland"
#let kunde_adresse = "Alter Wall 69"
#let kunde_plz_ort = "D - 20457 Hamburg"
#let kunde_hrb = "HRB. NR.: 181535 Hamburg"
#let kunde_ust = "UST.-IDNR.: DE310161615"

// Positionen: (Beschreibung, Menge, Einheit, Einzelpreis)
#let positionen = (
  ("Beratungsleistung remote", 34.00, "Ph", 105.00),
)

// Zahlungshinweis
#let skonto_text = "3% Skonto bei Sofortzahlung (1-2 Tage)"

// === FIRMENDATEN (fix) ===
#let firma_name = "BLAUWEISS-EDV LLC"
#let firma_adresse = "106 Stratford St"
#let firma_plz_ort = "Houston, TX 77006"
#let firma_land = "USA"
#let firma_telefon = "+1 832 517 1100"
#let firma_email = "info@blauweiss-edv.com"
#let firma_web = "www.blauweiss-edv.com"

// Bankverbindung
#let bank_name = "Raiba St. Florian/Schärding"
#let bank_iban = "AT46 2032 6000 0007 0623"
#let bank_bic = "RZOOAT2L522"
#let bank_hinweis = "Zahlungen treuhänderisch an M. Matejka bis Eröffnung US-Firmenkontos"

// === FARBEN ===
#let blau = rgb("#1e5a99")
#let gruen = rgb("#8dc63f")
#let cyan = rgb("#00b4d8")
#let hellcyan = rgb("#e0f7fa")

// === SEITENEINRICHTUNG ===
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 3cm, left: 2cm, right: 1.5cm),
  footer: [
    #set text(size: 8pt, fill: gray)
    #line(length: 100%, stroke: 0.5pt + gray)
    #v(3pt)
    #grid(
      columns: (1fr, 1fr, 1fr),
      align: (left, center, right),
      [#bank_name | BIC: #bank_bic],
      [IBAN: #bank_iban],
      [#firma_web],
    )
  ]
)

#set text(font: "Inter", size: 10pt)

// === HEADER MIT LOGO ===
#grid(
  columns: (1fr, auto),
  gutter: 1cm,
  [
    // Logo
    #image("logo-blauweiss.png", width: 6cm)
  ],
  [
    // Firmenadresse rechts
    #box(
      fill: hellcyan,
      inset: 10pt,
      radius: 3pt,
    )[
      #set text(size: 9pt)
      #strong[#firma_name]

      #firma_adresse \
      #firma_plz_ort \
      #firma_land

      #v(0.3cm)
      #text(fill: cyan)[#firma_telefon] \
      #text(fill: cyan)[#firma_email]
    ]
  ]
)

#v(1cm)

// === KUNDENADRESSE ===
#kunde_name \
#kunde_adresse \
#kunde_plz_ort \
#kunde_hrb \
#kunde_ust

#v(1cm)

// === RECHNUNGSTITEL ===
#grid(
  columns: (auto, auto),
  gutter: 2cm,
  [#strong[Rechnung:] #text(fill: cyan)[#rechnung_nr]],
  [#strong[Datum:] #text(fill: cyan)[#datum]],
)

#v(0.5cm)

// === HINWEIS BANKVERBINDUNG ===
#box(
  width: 100%,
  fill: rgb("#fff3cd"),
  inset: 8pt,
  radius: 3pt,
)[
  #text(size: 9pt)[
    *ACHTUNG!* Bitte berücksichtigen Sie die Bankverbindung: IBAN #bank_iban \
    #text(size: 8pt, fill: gray)[#bank_hinweis]
  ]
]

#v(0.5cm)

// === ANSCHREIBEN ===
Sehr geehrte Damen und Herren!

Bezugnehmend auf den Projektvertrag Nr. #strong[#projekt_nr] erlauben wir uns unter Beilage des Leistungsscheines folgende Positionen unter Zugrundelegung von Reverse Charge §13b UStG in Rechnung zu stellen:

#v(0.5cm)

// === POSITIONSTABELLE ===
#let gesamt = positionen.map(p => p.at(1) * p.at(3)).sum()

#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  align: (left, right, right, right),
  stroke: 0.5pt + gray,
  inset: 8pt,

  // Header
  table.header(
    [*Beschreibung*], [*Menge*], [*Einzelpreis*], [*Betrag*],
  ),

  // Positionen
  ..positionen.map(p => {
    let betrag = p.at(1) * p.at(3)
    (
      p.at(0),
      [#p.at(1) #p.at(2)],
      [à EUR #str(p.at(3))],
      [EUR #str(calc.round(betrag, digits: 2))],
    )
  }).flatten(),

  // Summe
  table.cell(colspan: 3, align: right)[*Gesamt*],
  [*EUR #str(calc.round(gesamt, digits: 2))*],
)

#v(0.5cm)

// === ZAHLUNGSBEDINGUNGEN ===
Wir bedanken uns für das Vertrauen, die gute Zusammenarbeit und sehen der Begleichung des Rechnungsbetrages unter den vereinbarten Zahlungsbedingungen an die genannte Bankverbindung entgegen.

Für die gegenständliche Rechnung:
- #skonto_text

#v(1cm)

Mit freundlichen Grüßen,

#v(1.5cm)

// Unterschriftsbereich
#line(length: 5cm, stroke: 0.5pt + gray)
#text(size: 8pt, fill: gray)[Autorisierte Unterschrift]

#v(0.5cm)

*Anlage:*
- Leistungsschein
- Digitale Signatur
