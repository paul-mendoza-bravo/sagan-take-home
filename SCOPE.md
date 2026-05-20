# Scope decisions — Sagan Take-Home (2-hour cap)

Explicit pre-build scoping. Captured before writing code so the tradeoffs are deliberate, not accidental.

## Will build (V1 demo)

- One hardcoded client in code (no UI to add clients)
- HTML form for dynamic balances:
  - Inflow ($), Outflow ($), Private Reserve current ($)
  - 2 retirement accounts with balance (owner per spouse)
  - 1 non-retirement account with balance
  - 1 trust with Zillow value
  - 1 liability with balance + interest rate
- Automated calculations (exact rules from the PRD):
  - Excess = Inflow − Outflow
  - Private Reserve Target = 6 × Outflow (insurance deductibles skipped in V1 — see Gaps)
  - Retirement Total per spouse = sum of retirement accounts owned by that spouse
  - Non-Retirement Total = sum of non-retirement accounts — **does not include trust** (Rebecca, 24:28)
  - Grand Total Net Worth = Retirement + Non-Retirement + Trust
  - Liabilities Total = separate display, **not subtracted from net worth** (Rebecca, 26:15)
- SACS PDF generation (page 1): header with client name + date, Inflow → Outflow → Private Reserve diagram, numbers in their visual positions
- TCC summary (page 2): retirement per spouse, trust, non-retirement, grand total, liabilities separate

## Won't build (deliberately, per 2h cap — called out honestly in the Loom)

- Client management UI (add/edit/delete)
- Full TCC bubble chart with variable bubble count (1–6 per spouse, Rebecca 22:00) — current TCC uses styled sections with correct data and grouping; full dynamic-positioned circle layout is V1.1
- Canva export
- Authentication
- Dropbox auto-save / report history
- Database with migrations (state is in-memory)
- Pixel-perfect visual match to the Canva template (legible and correct is enough for V1)

## Gaps noticed in the PRD

1. The "Data Point List" document referenced at timestamp 29:14 was not shared. Field mapping was inferred from the transcript and the sample PDFs.
2. The TCC has a variable bubble count (1–6 per spouse, Rebecca 22:00) — this needs a real dynamic layout strategy beyond a fixed grid, which wouldn't fit safely in the time cap.
3. The Private Reserve Target formula is documented as "6 × monthly expenses + sum of all insurance deductibles" — insurance deductibles were not modeled in V1. Worth clarifying with Rebecca how deductibles are stored per client.
