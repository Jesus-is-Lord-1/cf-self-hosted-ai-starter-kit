#!/usr/bin/env python3
"""
Underwriting model — 170 Michaela Dr, Alpharetta, GA 30009
6bd / 5.5ba / 5,120 sqft new construction (2025) on 0.6 acre, Wills Park / downtown Alpharetta.

Strategy modeled: discounted acquisition of a distressed spec home (11 months on market,
$2.695M -> $2.15M ask), furnished executive lease during hold, resale into the 2027
spring selling season. Also computes the rejected buy-and-hold rental case (DSCR test)
and the LP-syndication vs. Co-GP/JV return split.

All market inputs are sourced in MARKET_DATA.md (research as of July 2026).
Run: python3 underwriting_model.py > outputs/scenarios.md
"""

SQFT = 5_120

# ---------------------------------------------------------------- assumptions
ASK_PRICE = 2_150_000          # confirmed current ask (relisted, was $2,695,000)

# Financing (mid-2026 sourced rates)
BRIDGE_LTC = 0.65              # stabilized-bridge on finished new construction
BRIDGE_RATE = 0.095            # 9.5% IO (between DSCR ~7.5% and hard money ~10.2% Atlanta avg)
BRIDGE_POINTS = 0.02
DSCR_RATE = 0.0725             # for the rejected hold case
CASHOUT_REFI_RATE = 0.0775     # investor cash-out, 75% LTV cap (contingency plan)

# Acquisition / carry / exit costs
ACQ_CLOSING_PCT = 0.0125       # title, transfer, legal, inspection
FURNISH_STAGE = 50_000         # furnish once: enables exec lease AND staged sale
TAXES_YR = 20_000              # carry-period estimate: assessed basis lags sale; full
                               # reassessed non-homestead ~= $27k/yr at $2.15M FMV (31.7 mills x 40%)
INSURANCE_YR = 12_000          # high-value landlord policy estimate
UTILITIES_MO = 750             # utilities, lawn, alarm
SELL_COST_PCT = 0.055          # 5.0% commissions + 0.5% closing/concessions

# Furnished executive rental during hold (corporate demand: 900 tech firms, Avalon corridor)
EXEC_RENT_MO = 8_500           # furnished premium over $5.5-7.5k unfurnished market
LEASE_UP_MONTHS = 3            # vacant during reposition/lease-up
MGMT_PCT = 0.08

# Equity structure
LP_SHARE = 0.90                # LP funds 90% of equity, GP co-invests 10%
PREF = 0.08                    # 8% annual preferred, LP capital
PROMOTE_SPLIT_LP = 0.70        # post-pref profit split 70 LP / 30 GP
WORKING_CAPITAL = 25_000

JV_PREF = 0.10                 # JV alternative: capital partner 100% of equity
JV_SPLIT_CAPITAL = 0.60        # post-pref 60 capital / 40 operator, no fees


def underwrite(buy, exit_price, hold_mo, leveraged=True, rent=True, setup=FURNISH_STAGE):
    """Returns dict of deal economics for one scenario."""
    loan = BRIDGE_LTC * buy if leveraged else 0.0
    points = loan * BRIDGE_POINTS
    closing = buy * ACQ_CLOSING_PCT
    interest = loan * BRIDGE_RATE * hold_mo / 12

    carry = (TAXES_YR + INSURANCE_YR) * hold_mo / 12 + UTILITIES_MO * hold_mo
    rent_mo = max(0, hold_mo - LEASE_UP_MONTHS) if rent else 0
    rent_net = EXEC_RENT_MO * rent_mo * (1 - MGMT_PCT)

    total_cash = buy + closing + points + setup + WORKING_CAPITAL - loan
    sale_net = exit_price * (1 - SELL_COST_PCT)
    profit = (sale_net - loan) + rent_net - interest - carry - total_cash

    equity = total_cash + max(0.0, interest + carry - rent_net - WORKING_CAPITAL)
    roe = profit / equity
    ann = roe * 12 / hold_mo
    return dict(buy=buy, exit=exit_price, hold=hold_mo, loan=loan, equity=equity,
                profit=profit, roe=roe, ann=ann, sale_net=sale_net,
                interest=interest, carry=carry, rent_net=rent_net,
                closing=closing, points=points)


def waterfall(d):
    """LP syndication: 90/10 co-invest, 8% pref on LP capital, then 70/30."""
    lp_cap = d["equity"] * LP_SHARE
    gp_cap = d["equity"] * (1 - LP_SHARE)
    pref = lp_cap * PREF * d["hold"] / 12
    residual = max(0.0, d["profit"] - pref - gp_cap * PREF * d["hold"] / 12)
    lp_profit = pref + residual * PROMOTE_SPLIT_LP
    gp_profit = gp_cap * PREF * d["hold"] / 12 + residual * (1 - PROMOTE_SPLIT_LP)
    if d["profit"] < pref:  # pref not covered: LPs get all profit; GP co-invest is first-loss
        gp_profit = max(min(0.0, d["profit"]), -gp_cap)   # GP loss capped at its capital
        lp_profit = d["profit"] - gp_profit               # remaining loss (if any) hits LPs
    lp_ann = (lp_profit / lp_cap) * 12 / d["hold"]
    gp_ann = (gp_profit / gp_cap) * 12 / d["hold"] if gp_cap else 0
    return lp_cap, lp_profit, lp_ann, gp_cap, gp_profit, gp_ann


def jv(d):
    """JV: capital partner funds 100% equity, 10% pref, then 60/40 to capital/operator."""
    cap = d["equity"]
    pref = cap * JV_PREF * d["hold"] / 12
    residual = max(0.0, d["profit"] - pref)
    cap_profit = min(d["profit"], pref) + residual * JV_SPLIT_CAPITAL
    op_profit = residual * (1 - JV_SPLIT_CAPITAL)
    return cap, cap_profit, (cap_profit / cap) * 12 / d["hold"], op_profit


def rental_reject_case(buy=2_150_000):
    """Why buy-and-hold DSCR rental fails at the ask."""
    rent_yr = 6_500 * 12  # midpoint unfurnished
    noi = rent_yr - 27_000 - INSURANCE_YR - rent_yr * MGMT_PCT - 6_000  # taxes/ins/mgmt/maint
    cap = noi / buy
    out = [f"Gross rent $6,500/mo -> NOI ${noi:,.0f}/yr -> cap rate {cap:.2%} on ${buy:,.0f} ask"]
    for ltv in (0.60, 0.70, 0.75):
        debt_svc = buy * ltv * DSCR_RATE  # IO approximation, amortizing is worse
        out.append(f"  DSCR at {ltv:.0%} LTV / {DSCR_RATE:.2%}: {noi/debt_svc:.2f}  (lender floor 1.00-1.25)")
    return "\n".join(out)


def mao(exit_price, hold_mo, target_ann=0.18):
    """Maximum allowable offer: highest price hitting target annualized deal ROE."""
    lo, hi = 1_000_000, exit_price
    for _ in range(60):
        mid = (lo + hi) / 2
        if underwrite(mid, exit_price, hold_mo)["ann"] >= target_ann:
            lo = mid
        else:
            hi = mid
    return lo


def money(x): return f"${x:,.0f}"


def strategy_grid():
    """Full data export: strategies x price tiers x exit scenarios."""
    buys = [1_750_000, 1_825_000, 1_950_000]
    exits = [("bear", 2_050_000), ("base", 2_200_000), ("bull", 2_350_000)]
    out = {"sqft": SQFT, "ask": ASK_PRICE, "buys": buys, "strategies": {}}

    # Strategy A: staged vacant resale sprint (8 mo, staging only, no rent)
    # Strategy B: furnished executive carry -> spring exit (12 mo, rent offsets carry)
    # Strategy C: buy-hold-refi rental — rejected (DSCR fails); captured separately
    holds = {"A": {"bear": 10, "base": 8, "bull": 6}, "B": {"bear": 14, "base": 12, "bull": 10}}
    for strat, rent_on, setup in (("A", False, 25_000), ("B", True, 50_000)):
        rows = []
        for buy in buys:
            for tag, xp in exits:
                d = underwrite(buy, xp, holds[strat][tag], rent=rent_on, setup=setup)
                lc, lp, la, gc, gp_, ga = waterfall(d)
                c, cp, ca, op = jv(d)
                rows.append(dict(buy=buy, scenario=tag, exit=xp, hold=d["hold"],
                                 equity=round(d["equity"]), profit=round(d["profit"]),
                                 roe=round(d["roe"], 4), ann=round(d["ann"], 4),
                                 lp_capital=round(lc), lp_profit=round(lp), lp_ann=round(la, 4),
                                 gp_profit=round(gp_), gp_ann=round(ga, 4),
                                 jv_capital_profit=round(cp), jv_capital_ann=round(ca, 4),
                                 jv_operator_profit=round(op)))
        out["strategies"][strat] = rows
    return out


if __name__ == "__main__":
    print("# 170 Michaela Dr — Underwriting Output\n")
    print(f"Subject: 5,120 sqft | ask {money(ASK_PRICE)} (${ASK_PRICE/SQFT:,.0f}/sqft) | "
          f"comp support $420-470/sqft = {money(420*SQFT)}-{money(470*SQFT)}\n")

    print("## Rejected case: buy-and-hold DSCR rental at the ask\n```")
    print(rental_reject_case())
    print("```\nConclusion: DSCR ~0.3-0.4 — unfinanceable as a rental; cash flow cannot carry this asset.\n")

    BUY = 1_825_000
    scenarios = [
        ("BEAR — comp floor, slow exit",  underwrite(BUY, 2_050_000, 14)),
        ("BASE — mid-comp exit",          underwrite(BUY, 2_200_000, 12)),
        ("BULL — spring '27 premium",     underwrite(BUY, 2_350_000, 10)),
    ]
    t18 = mao(2_200_000, 12, 0.18)
    t15 = mao(2_200_000, 12, 0.15)
    print(f"## Maximum allowable offer (base exit {money(2_200_000)}, 12-mo hold)\n")
    print(f"- MAO @ 18% annualized deal ROE: **{money(t18)}** ({t18/SQFT:,.0f}/sqft)")
    print(f"- MAO @ 15% annualized deal ROE: **{money(t15)}** ({t15/SQFT:,.0f}/sqft)")
    print(f"- Recommended offer basis used below: **{money(BUY)}** "
          f"({BUY/SQFT:,.0f}/sqft, {1-BUY/ASK_PRICE:.1%} below ask)\n")

    print("## Scenarios (leveraged 65% LTC bridge @ 9.5% + 2pts, furnished exec lease during hold)\n")
    print("| Scenario | Buy | Exit | Hold | Equity | Profit | ROE | Annualized |")
    print("|---|---|---|---|---|---|---|---|")
    for name, d in scenarios:
        print(f"| {name} | {money(d['buy'])} | {money(d['exit'])} | {d['hold']} mo | "
              f"{money(d['equity'])} | {money(d['profit'])} | {d['roe']:.1%} | {d['ann']:.1%} |")

    print("\n## LP syndication waterfall (LP 90% of equity, 8% pref, 70/30 promote)\n")
    print("| Scenario | LP capital | LP profit | LP annualized | GP capital | GP profit | GP annualized |")
    print("|---|---|---|---|---|---|---|")
    for name, d in scenarios:
        lc, lp, la, gc, gp_, ga = waterfall(d)
        print(f"| {name} | {money(lc)} | {money(lp)} | {la:.1%} | {money(gc)} | {money(gp_)} | {ga:.1%} |")

    print("\n## JV alternative (capital partner 100% equity, 10% pref, 60/40, no fees)\n")
    print("| Scenario | Capital in | Capital profit | Capital annualized | Operator profit (sweat) |")
    print("|---|---|---|---|---|")
    for name, d in scenarios:
        c, cp, ca, op = jv(d)
        print(f"| {name} | {money(c)} | {money(cp)} | {ca:.1%} | {money(op)} |")

    print("\n## Base-case cash detail\n```")
    d = scenarios[1][1]
    for k in ("loan", "closing", "points", "interest", "carry", "rent_net", "sale_net", "equity", "profit"):
        print(f"{k:>10}: {money(d[k])}")
    print("```")

    print("\n## Contingency: refi-and-hold if exit market stalls (Plan B)")
    loan75 = 0.75 * 2_050_000
    ds = loan75 * CASHOUT_REFI_RATE
    rent_yr = EXEC_RENT_MO * 11 * (1 - MGMT_PCT)
    noi = rent_yr - 27_000 - INSURANCE_YR - 6_000
    print(f"- Investor cash-out at 75% of {money(2_050_000)} appraisal = {money(loan75)} @ {CASHOUT_REFI_RATE:.2%}")
    print(f"- Furnished NOI {money(noi)}/yr vs debt service {money(ds)}/yr -> DSCR {noi/ds:.2f}")
    print("- DSCR < 1.0 even furnished: refi-and-hold only works de-levered (<= ~55% LTV) or as")
    print("  negative-carry bridge to a delayed sale. Primary plan remains DISPOSITION; the true")
    print("  Plan B is: cut price to the $2.0-2.05M comp floor and clear — bear case already models this.")

    import json, os
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results.json", "w") as f:
        json.dump(strategy_grid(), f, indent=1)
    import sys
    print("\n(strategy grid exported to outputs/results.json)", file=sys.stderr)
