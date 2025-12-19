#!/usr/bin/env python3
"""
BLAUWEISS-EDV LLC – Rechnungsgenerator (Multilingual)
Erstellt Rechnungen basierend auf Zielregion und Sprachauswahl

Steuerliche Behandlung (Quelle: USA → Ziel):
- EU:       Reverse Charge Art. 196 MwStSystRL, USt-IdNr. Pflicht
- USA:      Keine VAT, ggf. Sales Tax (B2B Services meist exempt)
- Drittland: Keine EU-Reverse-Charge, lokale Regeln
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Pfad zum Template-Ordner
TEMPLATE_DIR = Path(__file__).parent / "finance/templates/invoices/typst"

# Zielregionen mit steuerlicher Behandlung
REGIONS = {
    "eu": {
        "name": "EU (Reverse Charge)",
        "description": "Art. 196 MwStSystRL – Steuerschuldnerschaft beim Empfänger",
        "vat_required": True,
        "reverse_charge": True,
        "default_currency": "EUR",
        "vat_note_de": "Reverse Charge gem. Art. 196 der Richtlinie 2006/112/EG – MwStSystRL",
        "vat_note_en": "VAT reverse charge per Article 196 of Directive 2006/112/EC",
    },
    "usa": {
        "name": "USA (keine VAT)",
        "description": "Keine Umsatzsteuer auf B2B-Dienstleistungen",
        "vat_required": False,
        "reverse_charge": False,
        "default_currency": "USD",
        "vat_note_de": None,
        "vat_note_en": None,
    },
    "third": {
        "name": "Drittland (CH, UK, etc.)",
        "description": "Keine EU-Reverse-Charge, steuerfreie Ausfuhr",
        "vat_required": False,
        "reverse_charge": False,
        "default_currency": "EUR",
        "vat_note_de": "Steuerfreie Ausfuhrlieferung / Dienstleistung an Drittland",
        "vat_note_en": "Tax-exempt export / service to third country",
    },
}

# Sprachen
LANGUAGES = {
    "de": {"name": "Deutsch", "code": "de"},
    "en": {"name": "English", "code": "en"},
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
        "region": "eu",
        "lang": "de",
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
            print("  ⚠️  Pflichtfeld!")


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


def waehle_region():
    """Lässt den Benutzer die Zielregion wählen"""
    print("\n🌍 Zielregion wählen (steuerliche Behandlung):")
    for i, (key, region) in enumerate(REGIONS.items(), 1):
        vat = "USt-IdNr. erforderlich" if region["vat_required"] else "keine USt-IdNr."
        print(f"   {i}. {region['name']}")
        print(f"      → {region['description']} ({vat})")

    while True:
        try:
            wahl = int(input("\nRegion wählen (1-3): "))
            if 1 <= wahl <= len(REGIONS):
                key = list(REGIONS.keys())[wahl - 1]
                return key, REGIONS[key]
            else:
                print("  ⚠️  Ungültige Auswahl!")
        except ValueError:
            print("  ⚠️  Bitte eine Nummer eingeben!")


def waehle_sprache():
    """Lässt den Benutzer die Sprache wählen"""
    print("\n🗣️  Sprache wählen:")
    for i, (key, lang) in enumerate(LANGUAGES.items(), 1):
        print(f"   {i}. {lang['name']}")

    while True:
        try:
            wahl = int(input("\nSprache wählen (1-2): "))
            if 1 <= wahl <= len(LANGUAGES):
                key = list(LANGUAGES.keys())[wahl - 1]
                return key, LANGUAGES[key]
            else:
                print("  ⚠️  Ungültige Auswahl!")
        except ValueError:
            print("  ⚠️  Bitte eine Nummer eingeben!")


def waehle_kunde(region_key, lang_key):
    """Lässt den Benutzer einen Kunden wählen oder neu eingeben"""
    # Filter Kunden nach Region
    passende = {k: v for k, v in KUNDEN.items() if v.get("region") == region_key}
    
    print(f"\n📋 Verfügbare Kunden ({REGIONS[region_key]['name']}):")
    alle_kunden = list(passende.items())
    for i, (key, kunde) in enumerate(alle_kunden, 1):
        print(f"   {i}. {kunde['name']}")
    print(f"   {len(alle_kunden) + 1}. Neuen Kunden eingeben")

    while True:
        try:
            wahl = int(input("\nKunde wählen (Nummer): "))
            if 1 <= wahl <= len(alle_kunden):
                key = alle_kunden[wahl - 1][0]
                return KUNDEN[key], key
            elif wahl == len(alle_kunden) + 1:
                return kunde_eingeben(region_key, lang_key), "neu"
            else:
                print("  ⚠️  Ungültige Auswahl!")
        except ValueError:
            print("  ⚠️  Bitte eine Nummer eingeben!")


def kunde_eingeben(region_key, lang_key):
    """Neuen Kunden manuell eingeben"""
    region = REGIONS[region_key]
    is_en = lang_key == "en"
    
    if is_en:
        print("\n📝 Enter new customer:")
        kunde = {
            "name": frage("   Company name", required=True),
            "adresse": frage("   Street address", required=True),
            "plz_ort": frage("   City / Postal code", required=True),
            "land": frage("   Country", required=True),
            "hrb": frage("   Registration (optional)", ""),
            "projekt_nr": frage("   Project No.", ""),
            "region": region_key,
            "lang": lang_key,
        }
        if region["vat_required"]:
            kunde["ust_id"] = frage("   VAT ID (required)", required=True)
    else:
        print("\n📝 Neuen Kunden eingeben:")
        kunde = {
            "name": frage("   Firmenname", required=True),
            "adresse": frage("   Straße", required=True),
            "plz_ort": frage("   PLZ + Ort", required=True),
            "land": frage("   Land", required=True),
            "hrb": frage("   Handelsregister", ""),
            "projekt_nr": frage("   Projekt-Nr.", ""),
            "region": region_key,
            "lang": lang_key,
        }
        if region["vat_required"]:
            kunde["ust_id"] = frage("   USt-IdNr. (Pflicht bei Reverse Charge)", required=True)
    
    return kunde


def positionen_eingeben(lang_key, currency):
    """Fragt nach den Rechnungspositionen"""
    is_en = lang_key == "en"
    
    if is_en:
        print(f"\n💰 Enter line items ({currency}):")
        remote_label = "Remote consulting services"
        onsite_label = "On-site consulting services"
        unit = "hrs"
    else:
        print(f"\n💰 Positionen eingeben ({currency}):")
        remote_label = "Beratungsleistung remote"
        onsite_label = "Beratungsleistung on-site"
        unit = "Ph"

    prompt = lambda t, d=None: frage_zahl(f"   {t}", d)
    
    remote_stunden = prompt("Remote hours" if is_en else "Remote-Stunden", 0)
    remote_preis = prompt(f"Hourly rate ({currency})" if is_en else f"Stundensatz ({currency})", 105)

    onsite_stunden = prompt("On-site hours" if is_en else "Onsite-Stunden", 0)
    onsite_preis = prompt(f"On-site rate ({currency})" if is_en else f"Onsite-Satz ({currency})", 120)

    positionen = []
    if remote_stunden > 0:
        positionen.append((remote_label, remote_stunden, unit, remote_preis))
    if onsite_stunden > 0:
        positionen.append((onsite_label, onsite_stunden, unit, onsite_preis))

    # Weitere Positionen?
    more_prompt = "\n   Add another item? (y/N): " if is_en else "\n   Weitere Position? (j/N): "
    while True:
        weitere = input(more_prompt).strip().lower()
        if weitere in ('j', 'y'):
            beschreibung = frage("   Description" if is_en else "   Beschreibung")
            menge = frage_zahl("   Quantity" if is_en else "   Menge")
            einheit = frage("   Unit" if is_en else "   Einheit", "pcs" if is_en else "Stk")
            preis = frage_zahl(f"   Unit price ({currency})" if is_en else f"   Einzelpreis ({currency})")
            positionen.append((beschreibung, menge, einheit, preis))
        else:
            break

    return positionen


def format_datum(lang_key):
    """Gibt aktuelles Datum formatiert zurück"""
    if lang_key == "de":
        datum = datetime.now().strftime("%d. %B %Y")
        for en, de in MONATE_DE.items():
            datum = datum.replace(en, de)
        return datum
    else:
        return datetime.now().strftime("%B %d, %Y")


def generiere_typst_code(rechnung_nr, datum, kunde, positionen, region_key, lang_key, currency):
    """Generiert den Typst-Code basierend auf Region und Sprache"""
    region = REGIONS[region_key]
    is_en = lang_key == "en"
    
    # Positionen formatieren
    pos_code = "(\n"
    for pos in positionen:
        pos_code += f'  ("{pos[0]}", {pos[1]:.2f}, "{pos[2]}", {pos[3]:.2f}),\n'
    pos_code += ")"

    # VAT-Hinweis
    vat_note = region["vat_note_en"] if is_en else region["vat_note_de"]
    
    # Texte basierend auf Sprache
    if is_en:
        texts = {
            "invoice": "Invoice",
            "date": "Date",
            "project": "Project",
            "description": "Description",
            "quantity": "Quantity",
            "unit_price": "Unit Price",
            "amount": "Amount",
            "total": "Total (net)" if region["reverse_charge"] else "Total Due",
            "greeting": "Dear Sir or Madam,",
            "intro": f"With reference to project contract no.",
            "intro2": ", please find below our invoice for services rendered:",
            "thanks": "We thank you for your trust and the good cooperation.",
            "payment": "Please remit the invoice amount to the bank account stated above.",
            "discount": "3% discount for immediate payment (1-2 days)",
            "regards": "Kind regards,",
            "signature": "Authorized Signature",
            "enclosure": "Enclosure:",
            "service_report": "Service Report",
            "digital_sig": "Digital Signature",
            "attention": "ATTENTION!",
            "bank_note": "Please note the bank details:",
            "vat_label": "VAT ID",
            "no_vat": "No VAT charged – reverse charge applies, customer is liable for VAT" if region["reverse_charge"] else "",
        }
    else:
        texts = {
            "invoice": "Rechnung",
            "date": "Datum",
            "project": "Projekt",
            "description": "Beschreibung",
            "quantity": "Menge",
            "unit_price": "Einzelpreis",
            "amount": "Betrag",
            "total": "Gesamt (netto)" if region["reverse_charge"] else "Gesamt",
            "greeting": "Sehr geehrte Damen und Herren!",
            "intro": f"Bezugnehmend auf den Projektvertrag Nr.",
            "intro2": " erlauben wir uns folgende Positionen in Rechnung zu stellen:",
            "thanks": "Wir bedanken uns für das Vertrauen und die gute Zusammenarbeit.",
            "payment": "Bitte überweisen Sie den Rechnungsbetrag an die genannte Bankverbindung.",
            "discount": "3% Skonto bei Sofortzahlung (1-2 Tage)",
            "regards": "Mit freundlichen Grüßen,",
            "signature": "Autorisierte Unterschrift",
            "enclosure": "Anlage:",
            "service_report": "Leistungsschein",
            "digital_sig": "Digitale Signatur",
            "attention": "ACHTUNG!",
            "bank_note": "Bitte berücksichtigen Sie die Bankverbindung:",
            "vat_label": "USt-IdNr.",
            "no_vat": "Kein Ausweis von Umsatzsteuer – Leistungsempfänger schuldet die Steuer" if region["reverse_charge"] else "",
        }

    # VAT-Box generieren
    vat_box = ""
    if vat_note:
        if is_en:
            vat_box = f'''
#box(width: 100%, fill: rgb("#f0f0f0"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *VAT Note:* {vat_note}
  ]
]

#v(0.5cm)
'''
        else:
            vat_box = f'''
#box(width: 100%, fill: rgb("#f0f0f0"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *Hinweis zur Umsatzsteuer:* {vat_note}
  ]
]

#v(0.5cm)
'''

    # Kunden-VAT-ID Zeile
    customer_vat_line = ""
    if region["vat_required"] and kunde.get("ust_id"):
        customer_vat_line = f'{texts["vat_label"]}: {kunde.get("ust_id", "")}'

    # Footer VAT-Hinweis
    footer_vat = ""
    if texts["no_vat"]:
        footer_vat = f'''
#text(size: 9pt, fill: gray)[
  {texts["no_vat"]} \\\\
  {texts["vat_label"]}: {kunde.get("ust_id", "")}
]
'''

    return f'''// =============================================================================
// BLAUWEISS-EDV LLC – {texts["invoice"]} {rechnung_nr}
// Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}
// Region: {region["name"]} | Language: {LANGUAGES[lang_key]["name"]}
// =============================================================================

// === DATA ===
#let invoice_nr = "{rechnung_nr}"
#let invoice_date = "{datum}"
#let project_nr = "{kunde.get('projekt_nr', '')}"
#let currency = "{currency}"

// Customer
#let customer_name = "{kunde['name']}"
#let customer_address = "{kunde['adresse']}"
#let customer_city = "{kunde['plz_ort']}"
#let customer_country = "{kunde.get('land', '')}"
#let customer_reg = "{kunde.get('hrb', '')}"
#let customer_vat = "{kunde.get('ust_id', '')}"

// Line items
#let items = {pos_code}

// === COMPANY DATA ===
#let company_name = "BLAUWEISS-EDV LLC"
#let company_address = "106 Stratford St"
#let company_city = "Houston, TX 77006"
#let company_country = "USA"
#let company_phone = "+1 832 517 1100"
#let company_email = "info@blauweiss-edv.com"
#let company_web = "www.blauweiss-edv.com"

// Bank
#let bank_name = "Raiba St. Florian/Schärding"
#let bank_iban = "AT46 2032 6000 0007 0623"
#let bank_bic = "RZOOAT2L522"
#let bank_note = "{"Payments held in trust by M. Matejka until US company account is opened" if is_en else "Zahlungen treuhänderisch an M. Matejka bis Eröffnung US-Firmenkontos"}"

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
      
      #company_address \\\\
      #company_city \\\\
      #company_country
      
      #v(0.3cm)
      #text(fill: cyan)[#company_phone] \\\\
      #text(fill: cyan)[#company_email]
    ]
  ]
)

#v(1cm)

// === CUSTOMER ===
#customer_name \\\\
#customer_address \\\\
#customer_city \\\\
#customer_country \\\\
#customer_reg \\\\
{customer_vat_line}

#v(1cm)

// === TITLE ===
#grid(
  columns: (auto, auto),
  gutter: 2cm,
  [#strong[{texts["invoice"]}:] #text(fill: cyan)[#invoice_nr]],
  [#strong[{texts["date"]}:] #text(fill: cyan)[#invoice_date]],
)

#v(0.5cm)

// === BANK NOTICE ===
#box(width: 100%, fill: rgb("#fff3cd"), inset: 8pt, radius: 3pt)[
  #text(size: 9pt)[
    *{texts["attention"]}* {texts["bank_note"]} IBAN #bank_iban \\\\
    #text(size: 8pt, fill: gray)[#bank_note]
  ]
]

#v(0.5cm)

// === LETTER ===
{texts["greeting"]}

{texts["intro"]} #strong[#project_nr]{texts["intro2"]}
{vat_box}
// === TABLE ===
#let total = items.map(p => p.at(1) * p.at(3)).sum()

#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  align: (left, right, right, right),
  stroke: 0.5pt + gray,
  inset: 8pt,
  table.header([*{texts["description"]}*], [*{texts["quantity"]}*], [*{texts["unit_price"]}*], [*{texts["amount"]}*]),
  ..items.map(p => {{
    let amt = p.at(1) * p.at(3)
    (p.at(0), [#p.at(1) #p.at(2)], [#currency #str(p.at(3))], [#currency #str(calc.round(amt, digits: 2))])
  }}).flatten(),
  table.cell(colspan: 3, align: right)[*{texts["total"]}*],
  [*#currency #str(calc.round(total, digits: 2))*],
)

#v(0.3cm)
{footer_vat}
#v(0.5cm)

{texts["thanks"]}

- {texts["discount"]}

#v(1cm)

{texts["regards"]}

#v(1.5cm)

#line(length: 5cm, stroke: 0.5pt + gray)
#text(size: 8pt, fill: gray)[{texts["signature"]}]

#v(0.5cm)

*{texts["enclosure"]}*
- {texts["service_report"]}
- {texts["digital_sig"]}
'''


def main():
    print("=" * 60)
    print("🧾 BLAUWEISS-EDV LLC – Invoice Generator")
    print("   Source: USA → Destination: ???")
    print("=" * 60)

    # Prüfen ob Template existiert
    if not TEMPLATE_DIR.exists():
        print(f"\n❌ Template folder not found: {TEMPLATE_DIR}")
        sys.exit(1)

    # 1. Zielregion wählen (steuerliche Behandlung)
    region_key, region = waehle_region()
    
    # 2. Sprache wählen
    lang_key, lang = waehle_sprache()
    is_en = lang_key == "en"
    
    # 3. Währung
    currency = region["default_currency"]
    new_currency = frage(
        f"\n💱 {'Currency' if is_en else 'Währung'}", 
        currency
    )
    if new_currency:
        currency = new_currency.upper()

    # 4. Rechnungsdaten
    print(f"\n📄 {'Invoice data' if is_en else 'Rechnungsdaten'}:")
    rechnung_nr = frage(
        f"   {'Invoice number' if is_en else 'Rechnungsnummer'}", 
        f"OP_AR{datetime.now().strftime('%j')}_{datetime.now().year}"
    )
    datum = frage(
        f"   {'Date' if is_en else 'Datum'}", 
        format_datum(lang_key)
    )

    # 5. Kunde wählen
    kunde, kunde_key = waehle_kunde(region_key, lang_key)

    # 6. Positionen
    positionen = positionen_eingeben(lang_key, currency)

    if not positionen:
        print(f"\n❌ {'No line items!' if is_en else 'Keine Positionen!'}")
        sys.exit(1)

    # 7. Zusammenfassung
    gesamt = sum(p[1] * p[3] for p in positionen)
    print("\n" + "=" * 60)
    print(f"📋 {'SUMMARY' if is_en else 'ZUSAMMENFASSUNG'}")
    print("=" * 60)
    print(f"   {'Region' if is_en else 'Region'}:    {region['name']}")
    print(f"   {'Language' if is_en else 'Sprache'}:  {lang['name']}")
    print(f"   {'Invoice' if is_en else 'Rechnung'}: {rechnung_nr}")
    print(f"   {'Date' if is_en else 'Datum'}:     {datum}")
    print(f"   {'Customer' if is_en else 'Kunde'}:   {kunde['name']}")
    if region["vat_required"]:
        print(f"   {'VAT ID' if is_en else 'USt-IdNr.'}:  {kunde.get('ust_id', 'N/A')}")
    print(f"   {'Items' if is_en else 'Positionen'}:")
    for pos in positionen:
        print(f"      - {pos[0]}: {pos[1]} {pos[2]} × {currency} {pos[3]} = {currency} {pos[1] * pos[3]:.2f}")
    print(f"   {'TOTAL' if is_en else 'GESAMT'}:    {currency} {gesamt:.2f}")
    if region["vat_note_en" if is_en else "vat_note_de"]:
        print(f"   VAT: {region['vat_note_en' if is_en else 'vat_note_de']}")
    print("=" * 60)

    # 8. Bestätigung
    confirm = input(f"\n{'Create invoice? (Y/n)' if is_en else 'Rechnung erstellen? (J/n)'}: ").strip().lower()
    if confirm == 'n':
        print(f"❌ {'Cancelled.' if is_en else 'Abgebrochen.'}")
        sys.exit(0)

    # 9. Dateiname
    datum_kurz = datetime.now().strftime("%Y-%m-%d")
    kunde_kurz = kunde_key if kunde_key != "neu" else kunde['name'].split()[0].lower()
    prefix = "Invoice" if is_en else "Rechnung"
    dateiname = f"{datum_kurz}_{prefix}_{kunde_kurz}_{rechnung_nr.replace('OP_', '')}_{lang_key}.typ"
    dateipfad = TEMPLATE_DIR / dateiname

    # 10. Generieren
    inhalt = generiere_typst_code(rechnung_nr, datum, kunde, positionen, region_key, lang_key, currency)

    with open(dateipfad, 'w', encoding='utf-8') as f:
        f.write(inhalt)

    print(f"\n✅ {'Invoice created' if is_en else 'Rechnung erstellt'}: {dateipfad}")

    # 11. Git commit?
    commit_prompt = f"\n{'Commit and push? (Y/n)' if is_en else 'Committen und pushen? (J/n)'}: "
    if input(commit_prompt).strip().lower() != 'n':
        repo_root = Path(__file__).parent.resolve()

        try:
            print("\n⏳ Git add...")
            subprocess.run(['git', 'add', str(dateipfad)], cwd=repo_root, check=True)

            print("⏳ Git commit...")
            subprocess.run(
                ['git', 'commit', '-m', f'{prefix} {rechnung_nr} for {kunde["name"]} ({region_key.upper()}/{lang_key.upper()})'],
                cwd=repo_root,
                check=True
            )

            print("⏳ Git push...")
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=repo_root, check=True)

            print(f"\n🚀 {'Pushed! Pipeline running...' if is_en else 'Gepusht! Pipeline läuft...'}")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Git error: {e}")
            print(f"   git add '{dateipfad}'")
            print(f"   git commit -m '{prefix} {rechnung_nr}'")
            print("   git push origin main")


if __name__ == "__main__":
    main()
