#!/usr/bin/env python3
"""
BLAUWEISS-EDV LLC – Rechnungsgenerator
Erstellt eine neue Rechnung aus dem Typst-Template
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Pfad zum Template-Ordner
TEMPLATE_DIR = Path(__file__).parent / "finance/templates/invoices/typst"
TEMPLATE_FILE = TEMPLATE_DIR / "rechnung-template.typ"

# Vordefinierte Kunden (können erweitert werden)
KUNDEN = {
    "nemensis": {
        "name": "nemensis AG Deutschland",
        "adresse": "Alter Wall 69",
        "plz_ort": "D - 20457 Hamburg",
        "hrb": "HRB. NR.: 181535 Hamburg",
        "ust": "UST.-IDNR.: DE310161615",
        "projekt_nr": "00003151",
    },
    # Weitere Kunden hier hinzufügen...
}

def frage(text, default=None):
    """Fragt nach Eingabe mit optionalem Default-Wert"""
    if default:
        eingabe = input(f"{text} [{default}]: ").strip()
        return eingabe if eingabe else default
    else:
        while True:
            eingabe = input(f"{text}: ").strip()
            if eingabe:
                return eingabe
            print("  ⚠️  Bitte einen Wert eingeben!")

def frage_zahl(text, default=None):
    """Fragt nach einer Zahl"""
    while True:
        try:
            if default is not None:
                eingabe = input(f"{text} [{default}]: ").strip()
                return float(eingabe) if eingabe else default
            else:
                eingabe = input(f"{text}: ").strip()
                return float(eingabe)
        except ValueError:
            print("  ⚠️  Bitte eine gültige Zahl eingeben!")

def waehle_kunde():
    """Lässt den Benutzer einen Kunden wählen oder neu eingeben"""
    print("\n📋 Verfügbare Kunden:")
    for i, (key, kunde) in enumerate(KUNDEN.items(), 1):
        print(f"   {i}. {kunde['name']} ({key})")
    print(f"   {len(KUNDEN)+1}. Neuen Kunden eingeben")
    
    while True:
        try:
            wahl = int(input("\nKunde wählen (Nummer): "))
            if 1 <= wahl <= len(KUNDEN):
                key = list(KUNDEN.keys())[wahl-1]
                return KUNDEN[key], key
            elif wahl == len(KUNDEN)+1:
                return kunde_eingeben(), "neu"
            else:
                print("  ⚠️  Ungültige Auswahl!")
        except ValueError:
            print("  ⚠️  Bitte eine Nummer eingeben!")

def kunde_eingeben():
    """Neuen Kunden manuell eingeben"""
    print("\n📝 Neuen Kunden eingeben:")
    return {
        "name": frage("   Firmenname"),
        "adresse": frage("   Straße"),
        "plz_ort": frage("   PLZ + Ort"),
        "hrb": frage("   Handelsregister", ""),
        "ust": frage("   UST-ID", ""),
        "projekt_nr": frage("   Projekt-Nr.", ""),
    }

def positionen_eingeben():
    """Fragt nach den Rechnungspositionen"""
    print("\n💰 Positionen eingeben:")
    
    remote_stunden = frage_zahl("   Remote-Stunden", 0)
    remote_preis = frage_zahl("   Remote-Stundensatz (EUR)", 105)
    
    onsite_stunden = frage_zahl("   Onsite-Stunden", 0)
    onsite_preis = frage_zahl("   Onsite-Stundensatz (EUR)", 120)
    
    positionen = []
    if remote_stunden > 0:
        positionen.append(("Beratungsleistung remote", remote_stunden, "Ph", remote_preis))
    if onsite_stunden > 0:
        positionen.append(("Beratungsleistung on-site", onsite_stunden, "Ph", onsite_preis))
    
    # Weitere Positionen?
    while True:
        weitere = input("\n   Weitere Position hinzufügen? (j/N): ").strip().lower()
        if weitere == 'j':
            beschreibung = frage("   Beschreibung")
            menge = frage_zahl("   Menge")
            einheit = frage("   Einheit", "Stk")
            preis = frage_zahl("   Einzelpreis (EUR)")
            positionen.append((beschreibung, menge, einheit, preis))
        else:
            break
    
    return positionen

def generiere_rechnung(rechnung_nr, datum, kunde, positionen):
    """Generiert die Typst-Datei"""
    
    # Positionen als Typst-Code formatieren
    pos_code = "(\n"
    for pos in positionen:
        pos_code += f'  ("{pos[0]}", {pos[1]:.2f}, "{pos[2]}", {pos[3]:.2f}),\n'
    pos_code += ")"
    
    inhalt = f'''// =============================================================================
// BLAUWEISS-EDV LLC – Rechnung {rechnung_nr}
// Generiert am {datetime.now().strftime("%Y-%m-%d %H:%M")}
// =============================================================================

// === RECHNUNGSDATEN ===
#let rechnung_nr = "{rechnung_nr}"
#let datum = "{datum}"
#let projekt_nr = "{kunde.get('projekt_nr', '')}"

// Kunde
#let kunde_name = "{kunde['name']}"
#let kunde_adresse = "{kunde['adresse']}"
#let kunde_plz_ort = "{kunde['plz_ort']}"
#let kunde_hrb = "{kunde.get('hrb', '')}"
#let kunde_ust = "{kunde.get('ust', '')}"

// Positionen: (Beschreibung, Menge, Einheit, Einzelpreis)
#let positionen = {pos_code}

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

#set text(font: "Helvetica", size: 10pt)

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
      
      #firma_adresse \\
      #firma_plz_ort \\
      #firma_land
      
      #v(0.3cm)
      #text(fill: cyan)[#firma_telefon] \\
      #text(fill: cyan)[#firma_email]
    ]
  ]
)

#v(1cm)

// === KUNDENADRESSE ===
#kunde_name \\
#kunde_adresse \\
#kunde_plz_ort \\
#kunde_hrb \\
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
    *ACHTUNG!* Bitte berücksichtigen Sie die Bankverbindung: IBAN #bank_iban \\
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
  ..positionen.map(p => {{
    let betrag = p.at(1) * p.at(3)
    (
      p.at(0),
      [#p.at(1) #p.at(2)],
      [à EUR #str(p.at(3))],
      [EUR #str(calc.round(betrag, digits: 2))],
    )
  }}).flatten(),
  
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
'''
    return inhalt

def main():
    print("=" * 60)
    print("🧾 BLAUWEISS-EDV LLC – Rechnungsgenerator")
    print("=" * 60)
    
    # Prüfen ob Template existiert
    if not TEMPLATE_DIR.exists():
        print(f"\n❌ Template-Ordner nicht gefunden: {TEMPLATE_DIR}")
        print("   Bitte aus dem corporate-Repository ausführen!")
        sys.exit(1)
    
    # Rechnungsdaten sammeln
    print("\n📄 Rechnungsdaten:")
    rechnung_nr = frage("   Rechnungsnummer", f"OP_AR{datetime.now().strftime('%j')}_{datetime.now().year}")
    datum = frage("   Datum", datetime.now().strftime("%d. %B %Y").replace("January", "Januar").replace("February", "Februar").replace("March", "März").replace("April", "April").replace("May", "Mai").replace("June", "Juni").replace("July", "Juli").replace("August", "August").replace("September", "September").replace("October", "Oktober").replace("November", "November").replace("December", "Dezember"))
    
    # Kunde wählen
    kunde, kunde_key = waehle_kunde()
    
    # Positionen
    positionen = positionen_eingeben()
    
    if not positionen:
        print("\n❌ Keine Positionen eingegeben!")
        sys.exit(1)
    
    # Zusammenfassung
    gesamt = sum(p[1] * p[3] for p in positionen)
    print("\n" + "=" * 60)
    print("📋 ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"   Rechnung:  {rechnung_nr}")
    print(f"   Datum:     {datum}")
    print(f"   Kunde:     {kunde['name']}")
    print(f"   Positionen:")
    for pos in positionen:
        print(f"      - {pos[0]}: {pos[1]} {pos[2]} × €{pos[3]} = €{pos[1]*pos[3]:.2f}")
    print(f"   GESAMT:    €{gesamt:.2f}")
    print("=" * 60)
    
    # Bestätigung
    if input("\nRechnung erstellen? (J/n): ").strip().lower() == 'n':
        print("❌ Abgebrochen.")
        sys.exit(0)
    
    # Dateiname generieren
    datum_kurz = datetime.now().strftime("%Y-%m-%d")
    kunde_kurz = kunde_key if kunde_key != "neu" else kunde['name'].split()[0].lower()
    dateiname = f"{datum_kurz}_Invoice_{kunde_kurz}_{rechnung_nr.replace('OP_', '')}.typ"
    dateipfad = TEMPLATE_DIR / dateiname
    
    # Generieren
    inhalt = generiere_rechnung(rechnung_nr, datum, kunde, positionen)
    
    with open(dateipfad, 'w', encoding='utf-8') as f:
        f.write(inhalt)
    
    print(f"\n✅ Rechnung erstellt: {dateipfad}")
    print("\n📌 Nächste Schritte:")
    print(f"   1. git add {dateipfad}")
    print(f"   2. git commit -m 'Invoice {rechnung_nr}'")
    print(f"   3. git push origin main")
    print("   4. Pipeline generiert PDF → Git + Google Drive")
    
    # Optional: Direkt committen?
    if input("\nJetzt committen und pushen? (J/n): ").strip().lower() != 'n':
        os.chdir(TEMPLATE_DIR.parent.parent.parent.parent)  # zum repo root
        os.system(f'git add "{dateipfad}"')
        os.system(f'git commit -m "Invoice {rechnung_nr} for {kunde["name"]}"')
        os.system('git push origin main')
        print("\n🚀 Gepusht! Pipeline läuft...")

if __name__ == "__main__":
    main()
