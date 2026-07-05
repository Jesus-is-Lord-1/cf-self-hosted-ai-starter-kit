# 170 Michaela Dr, Alpharetta GA — Deal Package

Complete acquisition analysis for a 6bd/5.5ba, 5,120 sqft 2025 spec home near downtown
Alpharetta: 11 months on market, cut from $2.695M to $2.15M, with closed-comp support at
$420–470/sqft. Thesis: distressed-spec acquisition at **$1.75M** (max $1.80M), staged resale
with a furnished-executive-lease fallback. Researched July 2026.

## Designed presentations (Gamma)

Investor-grade visual versions of all three documents, built in Gamma (Lux theme), editable in your Gamma account:

| Deck | Edit / present | PDF download (expires ~1 week) |
|---|---|---|
| Market Breakdown | [gamma.app/docs/6prt21r5ss1rp18](https://gamma.app/docs/6prt21r5ss1rp18) | [PDF](https://assets.api.gamma.app/export/pdf/6prt21r5ss1rp18/db95985370a40aa435e53c80e72fc4ff/Alpharetta-30009-Market-Breakdown.pdf) |
| Strategy & Returns | [gamma.app/docs/7w4dpvg8zr1dyqo](https://gamma.app/docs/7w4dpvg8zr1dyqo) | [PDF](https://assets.api.gamma.app/export/pdf/7w4dpvg8zr1dyqo/e8364b5dec836d954d7b45c4446a6e52/170-Michaela-Drive-Strategy-andamp-Returns.pdf) |
| LP Pitch Deck | [gamma.app/docs/wi5ji1l421cg0is](https://gamma.app/docs/wi5ji1l421cg0is) | [PDF](https://assets.api.gamma.app/export/pdf/wi5ji1l421cg0is/8d4729128e4abc0039233b069c47d43c/170-Michaela-Drive-LP-Investment-Opportunity.pdf) |

Fresh PDF/PPTX exports can be generated anytime from the Gamma editor (Share → Export).

## Contents

| File | What it is |
|---|---|
| `01_market_breakdown.html` | Market presentation — Alpharetta/30009 vitals, subject timeline, comps, fundamentals, rental & carry economics, financing environment |
| `02_strategy_returns.html` | Strategy presentation — 4 strategies underwritten (staged resale, executive carry, rejected rental/refi, creative structures), lifecycle financing, sensitivity, MAO, risk register |
| `03_lp_pitch_deck.html` | LP pitch deck — opportunity, plan, sources & uses, waterfall, LP returns by scenario, LP-syndication vs single-partner-JV structures and roles, alignment, risks, terms |
| `underwriting.xlsx` | Formula-driven workbook: Assumptions → Deal Model → Scenarios → LP Waterfall → Rental-Refi Test → Comps & Market. Change any assumption; everything recalculates |
| `underwriting_model.py` | Python model that generated all numbers (`python3 underwriting_model.py > outputs/scenarios.md`) |
| `build_workbook.py` | Generates `underwriting.xlsx` (`python3 build_workbook.py`, needs `openpyxl`) |
| `MARKET_DATA.md` | Every sourced data point with links and confirmed-vs-estimate labels |
| `outputs/scenarios.md`, `outputs/results.json` | Model output: scenario tables and the full strategy × price × exit grid |

## Headline numbers (buy $1.75M, Track A base)

- All-in basis ~$375/sqft vs $420–470 comp band; equity ≈ $782K (LP $703K + GP $79K first-loss)
- Base: exit $2.2M in 8 mo → +$135K deal profit, 25.9% annualized; LP +$102.8K, 21.9% annualized
- Bear ($2.05M floor): LP capital returned whole, GP co-invest absorbs the loss
- Buy-and-hold rental **rejected**: 1.24% cap rate, DSCR 0.23–0.29 — the exit is a sale, priced accordingly

> Estimates for discussion, not an offer of securities. Verify subject status in FMLS before offering.
