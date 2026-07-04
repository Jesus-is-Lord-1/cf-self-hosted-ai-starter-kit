---
name: excel-dashboard-design
description: >
  Full-pipeline Excel dashboard builder in the exceltable.com style. Takes raw data through a Control pivot layer to finished DASHBOARD sheets with dark and light themes. Use whenever the user asks to make an Excel dashboard beautiful, build a dark-themed Excel dashboard, create an exceltable.com-style dashboard, beautify a spreadsheet, or turn raw data into a polished dashboard workbook. Output is always a downloadable .xlsx file.
---

# Excel Dashboard Design (exceltable.com style)

Build the ENTIRE pipeline every time: raw data → Control pivot sheet → DASHBOARD sheets. Never just style existing cells — architect the workbook.

## Sheet Architecture (in this order)

1. **Data** — raw records, one table, header row frozen. No formatting beyond a clean table.
2. **Control** — the pivot/aggregation layer. Every number shown on a dashboard is computed HERE (SUMIFS/COUNTIFS/pivot logic), never on the dashboard sheet itself. Dashboards reference Control cells only.
3. **Resources** — color swatches, theme constants, icon/shape reference, named ranges list.
4. **DASHBOARD** — dark theme, the primary deliverable.
5. **DASHBOARD Light** — identical layout, light theme.

## Color System

### Dark theme
- Canvas background: `#1F1F1F` to `#242430` range (fill entire visible grid, gridlines off)
- Card background: `#2A2A35`
- Card border/edge highlight: `#3A3A48`
- Primary accent: `#4FC3F7` (cyan-blue)
- Secondary accents: `#AB47BC` (purple), `#26C6DA` (teal), `#FFA726` (amber)
- Positive: `#66BB6A` · Negative: `#EF5350`
- Title text: `#FFFFFF` · Body text: `#B0B0C0` · Muted labels: `#7A7A8C`

### Light theme
- Canvas: `#F4F5F9`
- Card: `#FFFFFF` with soft gray border `#E1E4EC`
- Same accent hues, one shade darker for contrast (`#0288D1`, `#8E24AA`, `#00ACC1`, `#FB8C00`)
- Title text: `#1A1A2E` · Body: `#4A4A5A`

## Gradients (multi-stop, OOXML injection)

openpyxl only supports 2-stop gradients natively. For 3+ stop gradients (KPI cards, header bands), inject raw OOXML into the fill:

```python
from openpyxl.styles.fills import GradientFill
# 2-stop (native):
cell.fill = GradientFill(stop=("242430", "3A2A55"), degree=90)
```

For 3-stop: write the workbook, then patch `xl/styles.xml` — add `<gradientFill degree="90">` with three `<stop position="0/0.5/1">` children referencing hex colors, and point the cell's fill id at the new entry. Wrap in a helper; do not hand-edit per cell.

## Layout System

- Column width baseline: 2.5–3.0 (narrow grid). Build all cards on a fine grid of narrow columns and short rows so cards can be any size.
- Cards = merged-cell blocks with card background fill + thin border in card-edge color.
- Standard grid: header band (rows 1–3), KPI card row (4 cards across), two chart rows below.
- Gridlines OFF, headings OFF on dashboard sheets.

## Chart Types

- **KPI cards** — big number (28–36pt bold), label above (9pt caps, muted), delta below (▲ green / ▼ red)
- **Funnel** — horizontal bars, widest at top, stage labels left, values right
- **Pipeline bar** — stacked horizontal bar with stage segments in accent colors
- **Trend line** — smooth line, accent color, no gridlines, minimal axis, area fill at 15–20% opacity if supported
- All charts read from Control sheet ranges. Never from Data directly.

## Fonts & Shadows

- Font: Segoe UI (fallback Calibri). Titles 14–16pt semibold. Section labels 9pt ALL CAPS, letter-spaced feel via spacing cells.
- Shadow effect: simulate with a 1-row/1-col offset dark band (`#181820` dark theme / `#D8DBE4` light) behind each card.

## Theme Swap

DASHBOARD Light is generated programmatically from DASHBOARD: same cell layout and formulas, swap the color map. Keep one COLOR dict in the build script with `dark`/`light` keys — build both sheets from the same layout function.

## Build & Output

- Build with Python + openpyxl (Claude Code environment). 
- Always deliver a saved `.xlsx` file path.
- Validate before delivering: open the file with openpyxl read-only and confirm all 5 sheets exist and dashboard formulas resolve to Control references.
