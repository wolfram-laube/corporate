// =============================================================================
// BLAUWEISS-EDV LLC – Invoice Template (English, US Customers)
// =============================================================================
// Usage: Adjust variables at top, then `typst compile invoice.typ`
// No VAT applicable for US domestic B2B services
// =============================================================================

// === INVOICE DATA (adjust here) ===
#let invoice_nr = "OP_AR001_2025"
#let invoice_date = "December 19, 2025"
#let project_nr = "00003151"

// Customer
#let customer_name = "Example Corp."
#let customer_address = "123 Main Street, Suite 400"
#let customer_city = "Austin, TX 78701"
#let customer_country = "USA"
#let customer_ein = "XX-XXXXXXX"  // Customer's EIN (optional)

// Line items: (Description, Quantity, Unit, Unit Price)
#let line_items = (
  ("Remote consulting services", 184.00, "hrs", 105.00),
  ("On-site consulting services", 0.00, "hrs", 120.00),
)

// Payment terms
#let payment_terms = "Net 30"
#let discount_text = "3% discount for payment within 5 days"

// === COMPANY DATA (usually fixed) ===
#let company_name = "BLAUWEISS-EDV LLC"
#let company_address = "106 Stratford St"
#let company_city = "Houston, TX 77006"
#let company_country = "USA"
#let company_phone = "+1 832 517 1100"
#let company_email = "info@blauweiss-edv.com"
#let company_web = "www.blauweiss-edv.com"
#let company_ein = "XX-XXXXXXX"  // LLC's EIN (to be obtained)

// Bank details (fiduciary until US account opened)
#let bank_name = "Raiba St. Florian/Schärding"
#let bank_iban = "AT46 2032 6000 0007 0623"
#let bank_bic = "RZOOAT2L522"
#let bank_note = "Payments held in trust by M. Matejka until US company account is opened"

// === COLORS ===
#let blue = rgb("#1e5a99")
#let green = rgb("#8dc63f")
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

// === HEADER WITH LOGO ===
#grid(
  columns: (1fr, auto),
  gutter: 1cm,
  [
    // Logo
    #image("logo-blauweiss.png", width: 6cm)
  ],
  [
    // Company address on right
    #box(
      fill: light_cyan,
      inset: 10pt,
      radius: 3pt,
    )[
      #set text(size: 9pt)
      #strong[#company_name]
      
      #company_address \
      #company_city \
      #company_country
      
      #v(0.3cm)
      #text(fill: cyan)[#company_phone] \
      #text(fill: cyan)[#company_email]
      
      #v(0.2cm)
      #text(size: 8pt)[EIN: #company_ein]
    ]
  ]
)

#v(1cm)

// === CUSTOMER ADDRESS ===
#strong[Bill To:]

#customer_name \
#customer_address \
#customer_city \
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

// === BANK DETAILS NOTICE ===
#box(
  width: 100%,
  fill: rgb("#fff3cd"),
  inset: 8pt,
  radius: 3pt,
)[
  #text(size: 9pt)[
    *Payment Information:* Please remit to IBAN #bank_iban (BIC: #bank_bic) \
    #text(size: 8pt, fill: gray)[#bank_note]
  ]
]

#v(0.5cm)

// === LETTER TEXT ===
Dear Sir or Madam,

With reference to project contract no. #strong[#project_nr], please find below our invoice for services rendered:

#v(0.5cm)

// === LINE ITEMS TABLE ===
#let total = line_items.map(p => p.at(1) * p.at(3)).sum()

#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  align: (left, right, right, right),
  stroke: 0.5pt + gray,
  inset: 8pt,
  
  // Header
  table.header(
    [*Description*], [*Quantity*], [*Unit Price*], [*Amount*],
  ),
  
  // Line items
  ..line_items.map(p => {
    let amount = p.at(1) * p.at(3)
    (
      p.at(0),
      [#p.at(1) #p.at(2)],
      [USD #str(p.at(3))],
      [USD #str(calc.round(amount, digits: 2))],
    )
  }).flatten(),
  
  // Total
  table.cell(colspan: 3, align: right)[*Total Due*],
  [*USD #str(calc.round(total, digits: 2))*],
)

#v(0.5cm)

// === PAYMENT TERMS ===
Payment is due within 30 days of invoice date.

- #discount_text

#v(1cm)

Thank you for your business!

#v(1.5cm)

// Signature area
#line(length: 5cm, stroke: 0.5pt + gray)
#text(size: 8pt, fill: gray)[Authorized Signature]

#v(0.5cm)

*Enclosure:*
- Service Report
