#!/usr/bin/env python3
"""
BLAUWEISS-EDV LLC – Rechnungsgenerator (Multilingual)
Erstellt Rechnungen für EU- und US-Kunden in DE/EN
Reverse Charge nach Art. 196 MwStSystRL (Richtlinie 2006/112/EG)
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Pfad zum Template-Ordner
TEMPLATE_DIR = Path(__file__).parent / "finance/templates/invoices/typst"

# Invoice types
INVOICE_TYPES = {
    "de-eu": {
        "name": "Deutsch (EU-Kunden)",
        "template": "rechnung-de.typ",
        "currency": "EUR",
        "vat_required": True,
        "vat_note": "Reverse Charge gem. Art. 196 der Richtlinie 2006/112/EG – MwStSystRL",
    },
    "en-eu": {
        "name": "English (EU Customers)",
        "template": "invoice-en-eu.typ",
        "currency": "EUR",
        "vat_required": True,
        "vat_note": "VAT reverse charge per Article 196 of Directive 2006/112/EC",
    },
    "en-us": {
        "name": "English (US Customers)",
        "template": "invoice-en-us.typ",
        "currency": "USD",
        "vat_required": False,
        "vat_note": None,
    },
}

# Vordefinierte Kunden
KUNDEN = {
    "nemensis": {
        "name": "nemensis AG Deutschland",
        "adresse": "Alter Wall 69",
        "plz_ort": "D - 20457 Hamburg",
        "land": "Germany",
        "hrb": "HRB. NR.: 181535 Hamburg",
        "ust_id": "DE310161615",
        "projekt_nr": "00003151",
        "type": "de-eu",
    },
    # Weitere Kunden hier hinzufügen...
}

# Deutsche Monatsnamen
MONATE_DE = {
    "January": "Januar", "February": "Februar", "March": "März",
    "April": "April", "May": "Mai", "June": "Juni",
    "July": "Juli", "August": "August", "September": "September",
    "October": "Oktober", "November": "November", "December": "Dezember"
}


def frage(text, default=None, required=False):
    """Fragt nach Eingabe mit optionalem Default-Wert"""
    if default:
        eingabe = input(f"{text} [{default}]: ").strip()
        return eingabe if eingabe else default
    else:
        while True:
            eingabe = input(f"{text}: ").strip()
            if eingabe or not required:
                return eingabe
            print("  ⚠️  Pflichtfeld - bitte einen Wert eingeben!")


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


def waehle_typ():
    """Lässt den Benutzer den Rechnungstyp wählen"""
    print("\n🌍 Rechnungstyp wählen:")
    for i, (key, typ) in enumerate(INVOICE_TYPES.items(), 1):
        vat = "✓ USt-IdNr. erforderlich" if typ["vat_required"] else "keine USt"
        print(f"   {i}. {typ['name']} ({typ['currency']}, {vat})")

    while True:
        try:
            wahl = int(input("\nTyp wählen (Nummer): "))
            if 1 <= wahl <= len(INVOICE_TYPES):
                key = list(INVOICE_TYPES.keys())[wahl - 1]
                return key, INVOICE_TYPES[key]
            else:
                print("  ⚠️  Ungültige Auswahl!")
        except ValueError:
            print("  ⚠️  Bitte eine Nummer eingeben!")


def waehle_kunde(inv_type):
    """Lässt den Benutzer einen Kunden wählen oder neu eingeben"""
    # Filter Kunden nach Typ
    passende = {k: v for k, v in KUNDEN.items() if v.get("type") == inv_type}
    
    print(f"\n📋 Verfügbare Kunden ({INVOICE_TYPES[inv_type]['name']}):")
    alle_kunden = list(passende.items())
    for i, (key, kunde) in enumerate(alle_kunden, 1):
        print(f"   {i}. {kunde['name']} ({key})")
    print(f"   {len(alle_kunden) + 1}. Neuen Kunden eingeben")

    while True:
        try:
            wahl = int(input("\nKunde wählen (Nummer): "))
            if 1 <= wahl <= len(alle_kunden):
                key = alle_kunden[wahl - 1][0]
                return KUNDEN[key], key
            elif wahl == len(alle_kunden) + 1:
                return kunde_eingeben(inv_type), "neu"
            else:
                print("  ⚠️  Ungültige Auswahl!")
        except ValueError:
            print("  ⚠️  Bitte eine Nummer eingeben!")


def kunde_eingeben(inv_type):
    """Neuen Kunden manuell eingeben"""
    typ_info = INVOICE_TYPES[inv_type]
    
    if inv_type == "en-us":
        print("\n📝 Enter new customer (US):")
        return {
            "name": frage("   Company name", required=True),
            "adresse": frage("   Street address", required=True),
            "plz_ort": frage("   City, State ZIP", required=True),
            "land": "USA",
            "hrb": frage("   Registration (optional)", ""),
            "ein": frage("   EIN (optional)", ""),
            "projekt_nr": frage("   Project No.", ""),
            "type": inv_type,
        }
    elif inv_type == "en-eu":
        print("\n📝 Enter new customer (EU):")
        return {
            "name": frage("   Company name", required=True),
            "adresse": frage("   Street address", required=True),
            "plz_ort": frage("   Postal code + City", required=True),
            "land": frage("   Country", required=True),
            "hrb": frage("   Registration (optional)", ""),
            "ust_id": frage("   VAT ID (required for reverse charge)", required=True),
            "projekt_nr": frage("   Project No.", ""),
            "type": inv_type,
        }
    else:  # de-eu
        print("\n📝 Neuen Kunden eingeben (EU):")
        return {
            "name": frage("   Firmenname", required=True),
            "adresse": frage("   Straße", required=True),
            "plz_ort": frage("   PLZ + Ort", required=True),
            "land": frage("   Land", "Deutschland"),
            "hrb": frage("   Handelsregister", ""),
            "ust_id": frage("   USt-IdNr. (Pflicht bei Reverse Charge)", required=True),
            "projekt_nr": frage("   Projekt-Nr.", ""),
            "type": inv_type,
        }


def positionen_eingeben(inv_type):
    """Fragt nach den Rechnungspositionen"""
    typ_info = INVOICE_TYPES[inv_type]
    currency = typ_info["currency"]
    
    if inv_type.startswith("en"):
        print("\n💰 Enter line items:")
        remote_label = "Remote consulting services"
        onsite_label = "On-site consulting services"
        remote_prompt = "   Remote hours"
        onsite_prompt = "   On-site hours"
        rate_prompt = f"   Hourly rate ({currency})"
        more_prompt = "\n   Add another item? (y/N): "
        desc_prompt = "   Description"
        qty_prompt = "   Quantity"
        unit_prompt = "   Unit"
        price_prompt = f"   Unit price ({currency})"
    else:
        print("\n💰 Positionen eingeben:")
        remote_label = "Beratungsleistung remote"
        onsite_label = "Beratungsleistung on-site"
        remote_prompt = "   Remote-Stunden"
        onsite_prompt = "   Onsite-Stunden"
        rate_prompt = f"   Stundensatz ({currency})"
        more_prompt = "\n   Weitere Position hinzufügen? (j/N): "
        desc_prompt = "   Beschreibung"
        qty_prompt = "   Menge"
        unit_prompt = "   Einheit"
        price_prompt = f"   Einzelpreis ({currency})"

    remote_stunden = frage_zahl(remote_prompt, 0)
    remote_preis = frage_zahl(rate_prompt, 105)

    onsite_stunden = frage_zahl(onsite_prompt, 0)
    onsite_preis = frage_zahl(rate_prompt, 120)

    positionen = []
    if remote_stunden > 0:
        positionen.append((remote_label, remote_stunden, "hrs" if inv_type.startswith("en") else "Ph", remote_preis))
    if onsite_stunden > 0:
        positionen.append((onsite_label, onsite_stunden, "hrs" if inv_type.startswith("en") else "Ph", onsite_preis))

    # Weitere Positionen?
    while True:
        weitere = input(more_prompt).strip().lower()
        if weitere in ('j', 'y'):
            beschreibung = frage(desc_prompt)
            menge = frage_zahl(qty_prompt)
            einheit = frage(unit_prompt, "pcs" if inv_type.startswith("en") else "Stk")
            preis = frage_zahl(price_prompt)
            positionen.append((beschreibung, menge, einheit, preis))
        else:
            break

    return positionen


def generiere_rechnung_de_eu(rechnung_nr, datum, kunde, positionen):
    """Generiert deutsche EU-Rechnung mit Art. 196"""
    pos_code = "(\n"
    for pos in positionen:
        pos_code += f'  ("{pos[0]}", {pos[1]:.2f}, "{pos[2]}", {pos[3]:.2f}),\n'
    pos_code += ")"

    return f'''// =============================================================================
// BLAUWEISS-EDV LLC – Rechnung {rechnung_nr}
// Generiert am {datetime.now().strftime("%Y-%m-%d %H:%M")}
// Reverse Charge nach Art. 196 MwStSystRL (Richtlinie 2006/112/EG)
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
#let kunde_ust_id = "{kunde.get('ust_id', '')}"

// Positionen
#let positionen = {pos_code}

// Zahlungshinweis
#let skonto_text = "3% Skonto bei Sofortzahlung (1-2 Tage)"

// === FIRMENDATEN ===
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
  [#image("logo-blauweiss.png", width: 6cm)],
  [
    #box(fill: hellcyan, inset: 10pt, radius: 3pt)[
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
USt-IdNr.: #kunde_ust_id

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
#box(width: 100%, fill: rgb("#fff3cd"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *ACHTUNG!* Bitte berücksichtigen Sie die Bankverbindung: IBAN #bank_iban \\
    #text(size: 8pt, fill: gray)[#bank_hinweis]
  ]
]

#v(0.5cm)

// === ANSCHREIBEN ===
Sehr geehrte Damen und Herren!

Bezugnehmend auf den Projektvertrag Nr. #strong[#projekt_nr] erlauben wir uns unter Beilage des Leistungsscheines folgende Positionen in Rechnung zu stellen:

#v(0.3cm)

#box(width: 100%, fill: rgb("#f0f0f0"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *Hinweis zur Umsatzsteuer:* Steuerschuldnerschaft des Leistungsempfängers \\
    (Reverse Charge gem. Art. 196 der Richtlinie 2006/112/EG – MwStSystRL)
  ]
]

#v(0.5cm)

// === POSITIONSTABELLE ===
#let gesamt = positionen.map(p => p.at(1) * p.at(3)).sum()

#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  align: (left, right, right, right),
  stroke: 0.5pt + gray,
  inset: 8pt,
  table.header([*Beschreibung*], [*Menge*], [*Einzelpreis*], [*Betrag*]),
  ..positionen.map(p => {{
    let betrag = p.at(1) * p.at(3)
    (p.at(0), [#p.at(1) #p.at(2)], [à EUR #str(p.at(3))], [EUR #str(calc.round(betrag, digits: 2))])
  }}).flatten(),
  table.cell(colspan: 3, align: right)[*Gesamt (netto)*],
  [*EUR #str(calc.round(gesamt, digits: 2))*],
)

#v(0.3cm)

#text(size: 9pt, fill: gray)[
  Kein Ausweis von Umsatzsteuer – Leistungsempfänger schuldet die Steuer \\
  Kunden-USt-IdNr.: #kunde_ust_id
]

#v(0.5cm)

Wir bedanken uns für das Vertrauen und sehen der Begleichung des Rechnungsbetrages entgegen.

Für die gegenständliche Rechnung:
- #skonto_text

#v(1cm)

Mit freundlichen Grüßen,

#v(1.5cm)

#line(length: 5cm, stroke: 0.5pt + gray)
#text(size: 8pt, fill: gray)[Autorisierte Unterschrift]

#v(0.5cm)

*Anlage:*
- Leistungsschein
- Digitale Signatur
'''


def generiere_rechnung_en_eu(invoice_nr, date, customer, line_items):
    """Generates English EU invoice with Art. 196"""
    items_code = "(\n"
    for item in line_items:
        items_code += f'  ("{item[0]}", {item[1]:.2f}, "{item[2]}", {item[3]:.2f}),\n'
    items_code += ")"

    return f'''// =============================================================================
// BLAUWEISS-EDV LLC – Invoice {invoice_nr}
// Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}
// VAT Reverse Charge per Article 196 of Directive 2006/112/EC
// =============================================================================

// === INVOICE DATA ===
#let invoice_nr = "{invoice_nr}"
#let invoice_date = "{date}"
#let project_nr = "{customer.get('projekt_nr', '')}"

// Customer
#let customer_name = "{customer['name']}"
#let customer_address = "{customer['adresse']}"
#let customer_city = "{customer['plz_ort']}"
#let customer_country = "{customer.get('land', '')}"
#let customer_reg_nr = "{customer.get('hrb', '')}"
#let customer_vat_id = "{customer.get('ust_id', '')}"

// Line items
#let line_items = {items_code}

// Payment terms
#let discount_text = "3% discount for immediate payment (1-2 days)"

// === COMPANY DATA ===
#let company_name = "BLAUWEISS-EDV LLC"
#let company_address = "106 Stratford St"
#let company_city = "Houston, TX 77006"
#let company_country = "USA"
#let company_phone = "+1 832 517 1100"
#let company_email = "info@blauweiss-edv.com"
#let company_web = "www.blauweiss-edv.com"

// Bank details
#let bank_name = "Raiba St. Florian/Schärding"
#let bank_iban = "AT46 2032 6000 0007 0623"
#let bank_bic = "RZOOAT2L522"
#let bank_note = "Payments held in trust by M. Matejka until US company account is opened"

// === COLORS ===
#let blue = rgb("#1e5a99")
#let cyan = rgb("#00b4d8")
#let light_cyan = rgb("#e0f7fa")

// === PAGE SETUP ===
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
      [#company_web],
    )
  ]
)

#set text(font: "Inter", size: 10pt)

// === HEADER ===
#grid(
  columns: (1fr, auto),
  gutter: 1cm,
  [#image("logo-blauweiss.png", width: 6cm)],
  [
    #box(fill: light_cyan, inset: 10pt, radius: 3pt)[
      #set text(size: 9pt)
      #strong[#company_name]
      
      #company_address \\
      #company_city \\
      #company_country
      
      #v(0.3cm)
      #text(fill: cyan)[#company_phone] \\
      #text(fill: cyan)[#company_email]
    ]
  ]
)

#v(1cm)

// === CUSTOMER ADDRESS ===
#customer_name \\
#customer_address \\
#customer_city \\
#customer_country \\
#customer_reg_nr \\
VAT ID: #customer_vat_id

#v(1cm)

// === INVOICE TITLE ===
#grid(
  columns: (auto, auto),
  gutter: 2cm,
  [#strong[Invoice:] #text(fill: cyan)[#invoice_nr]],
  [#strong[Date:] #text(fill: cyan)[#invoice_date]],
)

#v(0.5cm)

#box(width: 100%, fill: rgb("#fff3cd"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *ATTENTION!* Please note the bank details: IBAN #bank_iban \\
    #text(size: 8pt, fill: gray)[#bank_note]
  ]
]

#v(0.5cm)

Dear Sir or Madam,

With reference to project contract no. #strong[#project_nr], we hereby invoice the following services:

#v(0.3cm)

#box(width: 100%, fill: rgb("#f0f0f0"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *VAT Note:* VAT reverse charge – customer to account for VAT \\
    (per Article 196 of Directive 2006/112/EC)
  ]
]

#v(0.5cm)

// === LINE ITEMS ===
#let total = line_items.map(p => p.at(1) * p.at(3)).sum()

#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  align: (left, right, right, right),
  stroke: 0.5pt + gray,
  inset: 8pt,
  table.header([*Description*], [*Quantity*], [*Unit Price*], [*Amount*]),
  ..line_items.map(p => {{
    let amount = p.at(1) * p.at(3)
    (p.at(0), [#p.at(1) #p.at(2)], [EUR #str(p.at(3))], [EUR #str(calc.round(amount, digits: 2))])
  }}).flatten(),
  table.cell(colspan: 3, align: right)[*Total (net)*],
  [*EUR #str(calc.round(total, digits: 2))*],
)

#v(0.3cm)

#text(size: 9pt, fill: gray)[
  No VAT charged – reverse charge applies, customer is liable for VAT \\
  Customer VAT ID: #customer_vat_id
]

#v(0.5cm)

We thank you for your trust. Please remit the invoice amount to the bank account stated above.

For this invoice:
- #discount_text

#v(1cm)

Kind regards,

#v(1.5cm)

#line(length: 5cm, stroke: 0.5pt + gray)
#text(size: 8pt, fill: gray)[Authorized Signature]

#v(0.5cm)

*Enclosure:*
- Service Report
- Digital Signature
'''


def generiere_rechnung_en_us(invoice_nr, date, customer, line_items):
    """Generates English US invoice (no VAT)"""
    items_code = "(\n"
    for item in line_items:
        items_code += f'  ("{item[0]}", {item[1]:.2f}, "{item[2]}", {item[3]:.2f}),\n'
    items_code += ")"

    return f'''// =============================================================================
// BLAUWEISS-EDV LLC – Invoice {invoice_nr}
// Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}
// US Domestic Invoice (no VAT applicable)
// =============================================================================

// === INVOICE DATA ===
#let invoice_nr = "{invoice_nr}"
#let invoice_date = "{date}"
#let project_nr = "{customer.get('projekt_nr', '')}"

// Customer
#let customer_name = "{customer['name']}"
#let customer_address = "{customer['adresse']}"
#let customer_city = "{customer['plz_ort']}"
#let customer_country = "{customer.get('land', 'USA')}"

// Line items
#let line_items = {items_code}

// Payment terms
#let payment_terms = "Net 30"
#let discount_text = "3% discount for payment within 5 days"

// === COMPANY DATA ===
#let company_name = "BLAUWEISS-EDV LLC"
#let company_address = "106 Stratford St"
#let company_city = "Houston, TX 77006"
#let company_country = "USA"
#let company_phone = "+1 832 517 1100"
#let company_email = "info@blauweiss-edv.com"
#let company_web = "www.blauweiss-edv.com"
#let company_ein = "XX-XXXXXXX"

// Bank details
#let bank_name = "Raiba St. Florian/Schärding"
#let bank_iban = "AT46 2032 6000 0007 0623"
#let bank_bic = "RZOOAT2L522"
#let bank_note = "Payments held in trust by M. Matejka until US company account is opened"

// === COLORS ===
#let cyan = rgb("#00b4d8")
#let light_cyan = rgb("#e0f7fa")

// === PAGE SETUP ===
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
      [#company_web],
    )
  ]
)

#set text(font: "Inter", size: 10pt)

// === HEADER ===
#grid(
  columns: (1fr, auto),
  gutter: 1cm,
  [#image("logo-blauweiss.png", width: 6cm)],
  [
    #box(fill: light_cyan, inset: 10pt, radius: 3pt)[
      #set text(size: 9pt)
      #strong[#company_name]
      
      #company_address \\
      #company_city \\
      #company_country
      
      #v(0.3cm)
      #text(fill: cyan)[#company_phone] \\
      #text(fill: cyan)[#company_email]
      
      #v(0.2cm)
      #text(size: 8pt)[EIN: #company_ein]
    ]
  ]
)

#v(1cm)

// === CUSTOMER ADDRESS ===
#strong[Bill To:]

#customer_name \\
#customer_address \\
#customer_city \\
#customer_country

#v(1cm)

// === INVOICE TITLE ===
#grid(
  columns: (auto, auto, auto),
  gutter: 1.5cm,
  [#strong[Invoice:] #text(fill: cyan)[#invoice_nr]],
  [#strong[Date:] #text(fill: cyan)[#invoice_date]],
  [#strong[Terms:] #payment_terms],
)

#v(0.5cm)

#box(width: 100%, fill: rgb("#fff3cd"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *Payment Information:* Please remit to IBAN #bank_iban (BIC: #bank_bic) \\
    #text(size: 8pt, fill: gray)[#bank_note]
  ]
]

#v(0.5cm)

Dear Sir or Madam,

With reference to project contract no. #strong[#project_nr], please find below our invoice for services rendered:

#v(0.5cm)

// === LINE ITEMS ===
#let total = line_items.map(p => p.at(1) * p.at(3)).sum()

#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  align: (left, right, right, right),
  stroke: 0.5pt + gray,
  inset: 8pt,
  table.header([*Description*], [*Quantity*], [*Unit Price*], [*Amount*]),
  ..line_items.map(p => {{
    let amount = p.at(1) * p.at(3)
    (p.at(0), [#p.at(1) #p.at(2)], [USD #str(p.at(3))], [USD #str(calc.round(amount, digits: 2))])
  }}).flatten(),
  table.cell(colspan: 3, align: right)[*Total Due*],
  [*USD #str(calc.round(total, digits: 2))*],
)

#v(0.5cm)

Payment is due within 30 days of invoice date.

- #discount_text

#v(1cm)

Thank you for your business!

#v(1.5cm)

#line(length: 5cm, stroke: 0.5pt + gray)
#text(size: 8pt, fill: gray)[Authorized Signature]

#v(0.5cm)

*Enclosure:*
- Service Report
'''


def format_datum_de():
    """Gibt aktuelles Datum auf Deutsch formatiert zurück"""
    datum = datetime.now().strftime("%d. %B %Y")
    for en, de in MONATE_DE.items():
        datum = datum.replace(en, de)
    return datum


def main():
    print("=" * 60)
    print("🧾 BLAUWEISS-EDV LLC – Invoice Generator (Multilingual)")
    print("=" * 60)

    # Prüfen ob Template existiert
    if not TEMPLATE_DIR.exists():
        print(f"\n❌ Template folder not found: {TEMPLATE_DIR}")
        print("   Please run from the corporate repository!")
        sys.exit(1)

    # 1. Rechnungstyp wählen
    inv_type, typ_info = waehle_typ()
    currency = typ_info["currency"]
    is_english = inv_type.startswith("en")

    # 2. Rechnungsdaten sammeln
    if is_english:
        print("\n📄 Invoice data:")
        rechnung_nr = frage("   Invoice number", f"OP_AR{datetime.now().strftime('%j')}_{datetime.now().year}")
        datum = frage("   Date", datetime.now().strftime("%B %d, %Y"))
    else:
        print("\n📄 Rechnungsdaten:")
        rechnung_nr = frage("   Rechnungsnummer", f"OP_AR{datetime.now().strftime('%j')}_{datetime.now().year}")
        datum = frage("   Datum", format_datum_de())

    # 3. Kunde wählen
    kunde, kunde_key = waehle_kunde(inv_type)

    # 4. Positionen
    positionen = positionen_eingeben(inv_type)

    if not positionen:
        print("\n❌ No line items entered!" if is_english else "\n❌ Keine Positionen eingegeben!")
        sys.exit(1)

    # 5. Zusammenfassung
    gesamt = sum(p[1] * p[3] for p in positionen)
    print("\n" + "=" * 60)
    print("📋 SUMMARY" if is_english else "📋 ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"   {'Invoice' if is_english else 'Rechnung'}:  {rechnung_nr}")
    print(f"   {'Date' if is_english else 'Datum'}:     {datum}")
    print(f"   {'Customer' if is_english else 'Kunde'}:  {kunde['name']}")
    if typ_info["vat_required"]:
        print(f"   {'VAT ID' if is_english else 'USt-IdNr.'}:  {kunde.get('ust_id', 'N/A')}")
    print(f"   {'Line items' if is_english else 'Positionen'}:")
    for pos in positionen:
        print(f"      - {pos[0]}: {pos[1]} {pos[2]} × {currency} {pos[3]} = {currency} {pos[1] * pos[3]:.2f}")
    print(f"   {'TOTAL' if is_english else 'GESAMT'}:    {currency} {gesamt:.2f}")
    if typ_info["vat_note"]:
        print(f"   VAT: {typ_info['vat_note']}")
    print("=" * 60)

    # 6. Bestätigung
    confirm_prompt = "\nCreate invoice? (Y/n): " if is_english else "\nRechnung erstellen? (J/n): "
    if input(confirm_prompt).strip().lower() == 'n':
        print("❌ Cancelled." if is_english else "❌ Abgebrochen.")
        sys.exit(0)

    # 7. Dateiname generieren
    datum_kurz = datetime.now().strftime("%Y-%m-%d")
    kunde_kurz = kunde_key if kunde_key != "neu" else kunde['name'].split()[0].lower()
    prefix = "Invoice" if is_english else "Rechnung"
    dateiname = f"{datum_kurz}_{prefix}_{kunde_kurz}_{rechnung_nr.replace('OP_', '')}.typ"
    dateipfad = TEMPLATE_DIR / dateiname

    # 8. Generieren
    if inv_type == "de-eu":
        inhalt = generiere_rechnung_de_eu(rechnung_nr, datum, kunde, positionen)
    elif inv_type == "en-eu":
        inhalt = generiere_rechnung_en_eu(rechnung_nr, datum, kunde, positionen)
    else:  # en-us
        inhalt = generiere_rechnung_en_us(rechnung_nr, datum, kunde, positionen)

    with open(dateipfad, 'w', encoding='utf-8') as f:
        f.write(inhalt)

    print(f"\n✅ {'Invoice created' if is_english else 'Rechnung erstellt'}: {dateipfad}")

    # 9. Optional: Direkt committen?
    commit_prompt = "\nCommit and push now? (Y/n): " if is_english else "\nJetzt committen und pushen? (J/n): "
    if input(commit_prompt).strip().lower() != 'n':
        repo_root = Path(__file__).parent.resolve()

        try:
            print("\n⏳ Git add...")
            subprocess.run(['git', 'add', str(dateipfad)], cwd=repo_root, check=True)

            print("⏳ Git commit...")
            subprocess.run(
                ['git', 'commit', '-m', f'{prefix} {rechnung_nr} for {kunde["name"]}'],
                cwd=repo_root,
                check=True
            )

            print("⏳ Git push...")
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=repo_root, check=True)

            print(f"\n🚀 {'Pushed! Pipeline running...' if is_english else 'Gepusht! Pipeline läuft...'}")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Git error: {e}")
            print("   Please commit manually:")
            print(f"   git add '{dateipfad}'")
            print(f"   git commit -m '{prefix} {rechnung_nr}'")
            print("   git push origin main")


if __name__ == "__main__":
    main()
