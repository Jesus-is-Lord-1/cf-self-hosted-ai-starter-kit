#!/usr/bin/env python3
"""Builds underwriting.xlsx for 170 Michaela Dr — fully formula-driven.
Change anything on the Assumptions sheet and every other sheet recalculates.
Run: python3 build_workbook.py
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

INK = "1C2B24"       # deep spruce
BRASS = "B08A3E"
PALE = "EFF2ED"
WARN = "FDECEA"
OK = "E8F3EC"

H = Font(bold=True, color="FFFFFF", size=11)
HFILL = PatternFill("solid", fgColor=INK)
SUB = Font(bold=True, color=INK, size=12)
LBL = Font(color="3A4A42")
BOLD = Font(bold=True)
MONEY = '$#,##0'
PCT = '0.0%'
thin = Side(style="thin", color="D5DAD3")
BORDER = Border(bottom=thin)


def sheet_header(ws, title, sub):
    ws["A1"] = title; ws["A1"].font = Font(bold=True, size=15, color=INK)
    ws["A2"] = sub; ws["A2"].font = Font(size=10, color="6B7A72", italic=True)


def style_table_header(ws, row, cols, start=1):
    for i, c in enumerate(cols, start=start):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font = H; cell.fill = HFILL
        cell.alignment = Alignment(horizontal="center", wrap_text=True)


wb = Workbook()

# ---------------------------------------------------------------- Assumptions
ws = wb.active; ws.title = "Assumptions"
sheet_header(ws, "170 Michaela Dr, Alpharetta GA 30009 — Underwriting Assumptions",
             "Edit ONLY this sheet (blue cells). All other sheets recalculate. Sources: MARKET_DATA.md, research as of July 2026.")
rows = [
    ("PROPERTY", None, None, None),
    ("Ask price (relisted Feb 2026; was $2,695,000 Aug 2025)", 2_150_000, MONEY, "Confirmed, FMLS 7719521"),
    ("Purchase price (offer basis)", 1_750_000, MONEY, "Recommended MAO — see Scenarios"),
    ("Square feet", 5_120, '#,##0', "6bd/5.5ba, 2025 build, 0.6 ac"),
    ("FINANCING (bridge acquisition loan)", None, None, None),
    ("Loan-to-cost (LTC)", 0.65, PCT, "Stabilized new-construction bridge"),
    ("Interest rate (interest-only)", 0.095, PCT, "Atlanta private bridge, mid-2026"),
    ("Origination points", 0.02, PCT, ""),
    ("ACQUISITION & SETUP", None, None, None),
    ("Closing costs (% of price)", 0.0125, PCT, "Title, legal, transfer, inspection"),
    ("Furnishing / staging budget", 50_000, MONEY, "Enables exec lease + staged sale"),
    ("Working capital reserve", 25_000, MONEY, ""),
    ("CARRY (annual unless noted)", None, None, None),
    ("Property taxes / yr (carry period)", 20_000, MONEY, "Assessed basis lags; ~$27k/yr fully reassessed non-homestead at $2.15M (31.7 mills x 40%)"),
    ("Insurance / yr (high-value landlord)", 12_000, MONEY, "Chubb/PURE-tier estimate"),
    ("Utilities + lawn + alarm / mo", 750, MONEY, ""),
    ("OPERATIONS (furnished executive lease)", None, None, None),
    ("Furnished executive rent / mo", 8_500, MONEY, "vs $5.5-7.5k unfurnished market"),
    ("Lease-up / vacant months", 3, '0', ""),
    ("Property management (% of rent)", 0.08, PCT, ""),
    ("Market rent unfurnished / mo (rental test)", 6_500, MONEY, "Comps ~$1.00-1.45/sqft"),
    ("EXIT", None, None, None),
    ("Exit price (base case)", 2_200_000, MONEY, "Comp support $420-470/sqft = $2.15-2.41M"),
    ("Hold months (base case)", 12, '0', ""),
    ("Selling costs (% of exit)", 0.055, PCT, "5.0% commissions + 0.5% closing"),
    ("EQUITY STRUCTURE — LP SYNDICATION", None, None, None),
    ("LP share of equity", 0.90, PCT, "GP co-invests 10%, first-loss"),
    ("LP preferred return (annualized)", 0.08, PCT, ""),
    ("LP share of post-pref profit", 0.70, PCT, "70/30 promote"),
    ("EQUITY STRUCTURE — JV ALTERNATIVE", None, None, None),
    ("JV capital-partner preferred", 0.10, PCT, "Partner funds 100% of equity"),
    ("JV capital share post-pref", 0.60, PCT, "60/40, no fees"),
    ("RENTAL / REFI TEST RATES", None, None, None),
    ("DSCR loan rate", 0.0725, PCT, "Mid-2026, 75-80% LTV programs"),
    ("Investor cash-out refi rate", 0.0775, PCT, "75% LTV cap"),
]
r = 4
ASM = {}  # label -> cell ref
for label, val, fmt, note in rows:
    if val is None and fmt is None:
        ws.cell(row=r, column=1, value=label).font = SUB
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=PALE)
        for c in range(2, 5):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=PALE)
    else:
        ws.cell(row=r, column=1, value=label).font = LBL
        v = ws.cell(row=r, column=2, value=val)
        v.number_format = fmt
        v.font = Font(bold=True, color="1F5CB0")
        v.fill = PatternFill("solid", fgColor="EAF1FB")
        ws.cell(row=r, column=3, value=note).font = Font(size=9, color="6B7A72")
        ASM[label.split(" (")[0]] = f"Assumptions!$B${r}"
    r += 1
ws.column_dimensions["A"].width = 46
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 60

A = {
    "ask": ASM["Ask price"], "buy": ASM["Purchase price"], "sqft": ASM["Square feet"],
    "ltc": ASM["Loan-to-cost"], "rate": ASM["Interest rate"], "pts": ASM["Origination points"],
    "close": ASM["Closing costs"], "furnish": ASM["Furnishing / staging budget"],
    "wc": ASM["Working capital reserve"], "tax": ASM["Property taxes / yr"],
    "ins": ASM["Insurance / yr"], "util": ASM["Utilities + lawn + alarm / mo"],
    "rent": ASM["Furnished executive rent / mo"], "leaseup": ASM["Lease-up / vacant months"],
    "mgmt": ASM["Property management"], "mktrent": ASM["Market rent unfurnished / mo"],
    "exit": ASM["Exit price"], "hold": ASM["Hold months"], "sell": ASM["Selling costs"],
    "lpshare": ASM["LP share of equity"], "pref": ASM["LP preferred return"],
    "lpsplit": ASM["LP share of post-pref profit"], "jvpref": ASM["JV capital-partner preferred"],
    "jvsplit": ASM["JV capital share post-pref"], "dscr_rate": ASM["DSCR loan rate"],
    "refi_rate": ASM["Investor cash-out refi rate"],
}

# ---------------------------------------------------------------- Deal Model
ws = wb.create_sheet("Deal Model")
sheet_header(ws, "Deal Model — Base Case (formula-driven)",
             "Strategy B: acquire at discount, furnished executive lease during hold, resale. Driven entirely by Assumptions.")
lines = [
    ("SOURCES & USES", None, None),
    ("Purchase price", f"={A['buy']}", MONEY),
    ("Closing costs", f"={A['buy']}*{A['close']}", MONEY),
    ("Bridge loan", f"={A['buy']}*{A['ltc']}", MONEY),
    ("Origination points", f"=B7*{A['pts']}", MONEY),
    ("Furnishing / staging", f"={A['furnish']}", MONEY),
    ("Working capital", f"={A['wc']}", MONEY),
    ("Total equity required (cash in)", "=B5+B6+B8+B9+B10-B7", MONEY),
    ("HOLD PERIOD", None, None),
    ("Interest (IO)", f"=B7*{A['rate']}*{A['hold']}/12", MONEY),
    ("Taxes + insurance (prorated)", f"=({A['tax']}+{A['ins']})*{A['hold']}/12", MONEY),
    ("Utilities / lawn / alarm", f"={A['util']}*{A['hold']}", MONEY),
    ("Executive lease income (net of mgmt)", f"=MAX(0,{A['hold']}-{A['leaseup']})*{A['rent']}*(1-{A['mgmt']})", MONEY),
    ("Net carry", "=B13+B14+B15-B16", MONEY),
    ("EXIT", None, None),
    ("Gross exit price", f"={A['exit']}", MONEY),
    ("Selling costs", f"=B19*{A['sell']}", MONEY),
    ("Loan payoff", "=B7", MONEY),
    ("Net sale proceeds to equity", "=B19-B20-B21", MONEY),
    ("RETURNS (deal level)", None, None),
    ("Total profit", "=B22-B11-B17", MONEY),
    ("Return on equity (hold period)", "=B24/B11", PCT),
    ("Annualized ROE", f"=B25*12/{A['hold']}", PCT),
    ("Equity multiple", "=1+B25", '0.00"x"'),
    ("Exit $/sqft", f"=B19/{A['sqft']}", '$#,##0'),
    ("Basis $/sqft (all-in cost / sqft)", f"=(B5+B6+B9+B13+B17)/{A['sqft']}", '$#,##0'),
]
r = 4
for label, f, fmt in lines:
    if f is None:
        ws.cell(row=r, column=1, value=label).font = SUB
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=PALE)
        ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor=PALE)
    else:
        ws.cell(row=r, column=1, value=label).font = LBL
        c = ws.cell(row=r, column=2, value=f); c.number_format = fmt; c.font = BOLD
        c.border = BORDER; ws.cell(row=r, column=1).border = BORDER
    r += 1
for row_i, bold_row in ((11, True), (24, True)):
    ws.cell(row=row_i, column=2).font = Font(bold=True, color=BRASS, size=12)
ws.column_dimensions["A"].width = 40; ws.column_dimensions["B"].width = 16

# ---------------------------------------------------------------- Scenarios
ws = wb.create_sheet("Scenarios")
sheet_header(ws, "Scenario Grid — 2 strategies x 3 purchase prices x 3 exits",
             "Strategy A: staged vacant resale sprint (no lease, faster exit). Strategy B: furnished executive carry into spring market. Buy/Exit/Hold columns are inputs; the rest are formulas.")
cols = ["Strategy", "Buy", "Exit scenario", "Exit price", "Hold (mo)", "Lease?", "Setup $",
        "Loan", "Equity", "Interest", "Carry (tax/ins/util)", "Lease income (net)",
        "Sale net", "Profit", "ROE", "Annualized ROE", "Exit $/sqft"]
style_table_header(ws, 4, cols)
data = []
for strat, lease, setup in (("A", 0, 25_000), ("B", 1, 50_000)):
    holds = {"Bear": 10, "Base": 8, "Bull": 6} if strat == "A" else {"Bear": 14, "Base": 12, "Bull": 10}
    for buy in (1_750_000, 1_825_000, 1_950_000):
        for tag, xp in (("Bear", 2_050_000), ("Base", 2_200_000), ("Bull", 2_350_000)):
            data.append((strat, buy, tag, xp, holds[tag], lease, setup))
r = 5
for strat, buy, tag, xp, hold, lease, setup in data:
    ws.cell(row=r, column=1, value=f"{strat}")
    ws.cell(row=r, column=2, value=buy).number_format = MONEY
    ws.cell(row=r, column=3, value=tag)
    ws.cell(row=r, column=4, value=xp).number_format = MONEY
    ws.cell(row=r, column=5, value=hold)
    ws.cell(row=r, column=6, value=lease)
    ws.cell(row=r, column=7, value=setup).number_format = MONEY
    ws.cell(row=r, column=8, value=f"=B{r}*{A['ltc']}").number_format = MONEY
    ws.cell(row=r, column=9, value=(f"=B{r}+B{r}*{A['close']}+H{r}*{A['pts']}+G{r}+{A['wc']}-H{r}")).number_format = MONEY
    ws.cell(row=r, column=10, value=f"=H{r}*{A['rate']}*E{r}/12").number_format = MONEY
    ws.cell(row=r, column=11, value=f"=({A['tax']}+{A['ins']})*E{r}/12+{A['util']}*E{r}").number_format = MONEY
    ws.cell(row=r, column=12, value=f"=F{r}*MAX(0,E{r}-{A['leaseup']})*{A['rent']}*(1-{A['mgmt']})").number_format = MONEY
    ws.cell(row=r, column=13, value=f"=D{r}*(1-{A['sell']})").number_format = MONEY
    ws.cell(row=r, column=14, value=f"=M{r}-H{r}+L{r}-J{r}-K{r}-I{r}").number_format = MONEY
    ws.cell(row=r, column=15, value=f"=N{r}/I{r}").number_format = PCT
    ws.cell(row=r, column=16, value=f"=O{r}*12/E{r}").number_format = PCT
    cell = ws.cell(row=r, column=16); cell.font = BOLD
    ws.cell(row=r, column=17, value=f"=D{r}/{A['sqft']}").number_format = '$#,##0'
    fill = OK if tag == "Bull" else (WARN if tag == "Bear" else None)
    if fill:
        for c in range(1, 18):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=fill)
    r += 1
for i, w in enumerate([9, 12, 12, 12, 9, 7, 10, 12, 12, 11, 15, 13, 12, 12, 9, 12, 10], start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A5"

# ---------------------------------------------------------------- LP Waterfall
ws = wb.create_sheet("LP Waterfall")
sheet_header(ws, "Equity Waterfall — LP Syndication vs. Single-Partner JV",
             "Left: LP syndication (90/10 co-invest, pref, promote; GP co-invest is FIRST-LOSS). Right: JV (partner funds 100%, pref, split, no fees). Pulls base case from Deal Model.")
wf = [
    ("LP SYNDICATION", None, None),
    ("Total equity (from Deal Model)", "='Deal Model'!B11", MONEY),
    ("Deal profit (from Deal Model)", "='Deal Model'!B24", MONEY),
    ("LP capital", f"=B5*{A['lpshare']}", MONEY),
    ("GP co-invest capital", "=B5-B7", MONEY),
    ("LP preferred (pro-rated for hold)", f"=B7*{A['pref']}*{A['hold']}/12", MONEY),
    ("GP pref on co-invest", f"=B8*{A['pref']}*{A['hold']}/12", MONEY),
    ("Residual after prefs", "=MAX(0,B6-B9-B10)", MONEY),
    ("LP total profit", f"=IF(B6<B9, B6-MAX(MIN(0,B6),-B8), B9+B11*{A['lpsplit']})", MONEY),
    ("GP total profit (promote + co-invest)", "=B6-B12", MONEY),
    ("LP return on capital (hold)", "=B12/B7", PCT),
    ("LP annualized", f"=B14*12/{A['hold']}", PCT),
    ("LP equity multiple", "=1+B14", '0.00"x"'),
    ("GP annualized on co-invest", f"=IF(B8=0,0,B13/B8*12/{A['hold']})", PCT),
]
r = 4
for label, f, fmt in wf:
    if f is None:
        ws.cell(row=r, column=1, value=label).font = SUB
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=PALE)
        ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor=PALE)
    else:
        ws.cell(row=r, column=1, value=label).font = LBL
        c = ws.cell(row=r, column=2, value=f); c.number_format = fmt; c.font = BOLD
    r += 1
jvf = [
    ("JV ALTERNATIVE", None, None),
    ("Capital partner funds (100% of equity)", "='Deal Model'!B11", MONEY),
    ("Deal profit", "='Deal Model'!B24", MONEY),
    ("Capital partner preferred", f"=E5*{A['jvpref']}*{A['hold']}/12", MONEY),
    ("Residual after pref", "=MAX(0,E6-E7)", MONEY),
    ("Capital partner total profit", f"=MIN(E6,E7)+E8*{A['jvsplit']}", MONEY),
    ("Operator profit (sweat equity)", "=E6-E9", MONEY),
    ("Capital partner annualized", f"=E9/E5*12/{A['hold']}", PCT),
    ("Capital partner equity multiple", "=1+E9/E5", '0.00"x"'),
]
r = 4
for label, f, fmt in jvf:
    if f is None:
        ws.cell(row=r, column=4, value=label).font = SUB
        ws.cell(row=r, column=4).fill = PatternFill("solid", fgColor=PALE)
        ws.cell(row=r, column=5).fill = PatternFill("solid", fgColor=PALE)
    else:
        ws.cell(row=r, column=4, value=label).font = LBL
        c = ws.cell(row=r, column=5, value=f); c.number_format = fmt; c.font = BOLD
    r += 1
roles = [
    ("ROLES", "LP Syndication", "Single-Partner JV"),
    ("Sourcing, negotiation, MAO discipline", "GP (sponsor)", "Operator"),
    ("Capital", "LPs 90% / GP 10% first-loss", "Capital partner 100%"),
    ("Debt guarantee / carve-outs", "GP", "Negotiated (usually operator)"),
    ("Asset & lease management", "GP", "Operator"),
    ("Disposition decision", "GP (LP consent on major)", "Joint / dual-approval"),
    ("Reporting", "Monthly to LPs", "Direct, shared dashboard"),
    ("Fees", "None (promote only)", "None (split only)"),
    ("Decision speed", "Fast (GP controls)", "Slower (two signatures)"),
    ("Best when", "Multiple passive checks $50-250k", "One relationship writes the whole check"),
]
r = 21
style_table_header(ws, r, ["Dimension", "LP Syndication", "Single-Partner JV"]); r += 1
for a, b, c in roles[1:]:
    ws.cell(row=r, column=1, value=a).font = LBL
    ws.cell(row=r, column=2, value=b)
    ws.cell(row=r, column=3, value=c)
    r += 1
ws.column_dimensions["A"].width = 38; ws.column_dimensions["B"].width = 30
ws.column_dimensions["C"].width = 16; ws.column_dimensions["D"].width = 36
ws.column_dimensions["E"].width = 16

# ---------------------------------------------------------------- Rental test
ws = wb.create_sheet("Rental-Refi Test")
sheet_header(ws, "Why Buy-and-Hold Rental is REJECTED (shown for discipline)",
             "The asset cannot carry itself as a rental at any financeable leverage — the thesis must be the sale, not the yield.")
rt = [
    ("Gross unfurnished rent / yr", f"={A['mktrent']}*12", MONEY),
    ("Taxes (fully reassessed, non-homestead)", "=27000", MONEY),
    ("Insurance", f"={A['ins']}", MONEY),
    ("Management", f"=B4*{A['mgmt']}", MONEY),
    ("Maintenance / reserves", "=6000", MONEY),
    ("NOI", "=B4-B5-B6-B7-B8", MONEY),
    ("Cap rate at ask price", f"=B9/{A['ask']}", '0.00%'),
]
r = 4
for label, f, fmt in rt:
    ws.cell(row=r, column=1, value=label).font = LBL
    c = ws.cell(row=r, column=2, value=f); c.number_format = fmt; c.font = BOLD
    r += 1
style_table_header(ws, 12, ["LTV", "Loan", "Debt service (IO)", "DSCR", "Lender floor"], start=1)
r = 13
for ltv in (0.60, 0.70, 0.75):
    ws.cell(row=r, column=1, value=ltv).number_format = PCT
    ws.cell(row=r, column=2, value=f"={A['ask']}*A{r}").number_format = MONEY
    ws.cell(row=r, column=3, value=f"=B{r}*{A['dscr_rate']}").number_format = MONEY
    c = ws.cell(row=r, column=4, value=f"=$B$9/C{r}"); c.number_format = '0.00'
    c.font = Font(bold=True, color="C0392B")
    ws.cell(row=r, column=5, value="1.00–1.25")
    r += 1
ws.cell(row=17, column=1, value="Refi contingency: 75% cash-out at 7.75% needs ~$119k/yr debt service vs ~$41k furnished NOI → DSCR 0.34. "
        "Plan B is a price cut to the $2.0–2.05M comp floor (bear case), not a hold.").font = Font(size=10, color="6B7A72")
ws.column_dimensions["A"].width = 40
for col in "BCDE": ws.column_dimensions[col].width = 16

# ---------------------------------------------------------------- Comps
ws = wb.create_sheet("Comps & Market")
sheet_header(ws, "Comparable Sales & Market Data (researched July 2026)",
             "Full sourcing in MARKET_DATA.md. Subject: 5,120 sqft new 2025 build; ask $2.15M = $420/sqft after -20% cut from $2.695M.")
style_table_header(ws, 4, ["Address", "Sold price", "Date", "SqFt", "$/SqFt", "Bd/Ba", "Built", "Notes"])
comps = [
    ("477 Michael Dr, 30009 (same pocket)", 2_025_000, "Aug 2025", 4_804, "=B5/D5", "5/4.5", 2024, "New construction; 92% of list, ~55 DOM — best comp"),
    ("2444 Tenor Ln, 30009 (Avalon-adj.)", 2_224_500, "May 2025", 3_506, "=B6/D6", "3/3.5", 2024, "Walkability premium, small format"),
    ("135 Von Lake Dr, 30004", 2_292_500, "Oct 2025", 7_300, "=B7/D7", "5/5.5", 2023, "1-acre; 95.6% of list, ~2.5 mo"),
    ("2863 Stirling Ridge Ct, 30004", 2_032_500, "Jun 2025", 5_510, "=B8/D8", "6/8", 2006, "Resale estate — absorption datum"),
    ("1070 Mid Broadwell Rd, 30004", 2_630_444, "Jun 2023", 4_822, "=B9/D9", "5/5.5", 2023, "High-water $/sqft precedent (2023)"),
    ("289 Milton Ave, 30009 (downtown)", 1_844_000, "Jun 2023", 4_617, "=B10/D10", "5/4", 2017, "Near-new resale, walkable"),
]
r = 5
for row in comps:
    for c, v in enumerate(row, start=1):
        cell = ws.cell(row=r, column=c, value=v)
        if c == 2: cell.number_format = MONEY
        if c == 4: cell.number_format = '#,##0'
        if c == 5: cell.number_format = '$#,##0'
    r += 1
facts = [
    ("SUBJECT TIMELINE", ""),
    ("Oct 2024 — lot/teardown acquired by builder", "$570,000"),
    ("Aug 2025 — listed (Ansley / Christie's, FMLS 7622905)", "$2,695,000 ($526/sqft)"),
    ("Feb 2026 — relisted, builder self-listing (FMLS 7719521)", "$2,150,000 ($420/sqft) — a 20.2% cut"),
    ("Jul 2026 — still ACTIVE; ~11 months cumulative market time", "possible further cut to ~$2.0M (unconfirmed)"),
    ("MARKET SNAPSHOT", ""),
    ("Comp support band (closed new construction)", "$420–470/sqft → $2.15M–$2.41M"),
    ("Alpharetta median sale price (2026)", "$724k–740k; 2.3 months supply; ~97% list-to-sale"),
    ("Alpharetta avg DOM 2025 / early 2026", "~34 days / ~21 days — subject is 10x+ over"),
    ("30009 median $/sqft (all housing)", "$303, down ~4.6% YoY"),
    ("Median household income (Alpharetta)", "~$147,000; ~900 tech firms; Milton HS 10/10"),
    ("Financing (mid-2026)", "Jumbo 6.6% | DSCR 7.0–7.5% | Bridge/HM ~9.5–10.2% + 2–3 pts | Cash-out 7.75%"),
    ("Rents: unfurnished / furnished exec", "$5.5–7.5k/mo / ~$8–11k/mo; thin depth above $7k"),
    ("Taxes non-homestead (31.7 mills x 40% AV)", "~$27k/yr at $2.15M FMV; insurance ~$12k/yr"),
]
r += 2
for label, v in facts:
    if not v:
        ws.cell(row=r, column=1, value=label).font = SUB
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=PALE)
    else:
        ws.cell(row=r, column=1, value=label).font = LBL
        ws.cell(row=r, column=2, value=v).font = BOLD
    r += 1
ws.column_dimensions["A"].width = 52
for col in "BCDEFG": ws.column_dimensions[col].width = 14
ws.column_dimensions["H"].width = 48

wb.save("underwriting.xlsx")
print("underwriting.xlsx written")
