# Sagan Take-Home: Mi Scope (2 horas cap)

## ✅ WILL BUILD (V1 demo)
- 1 cliente hardcodeado en código (no UI de añadir clientes)
- Form HTML para balances dinámicos:
  - Inflow ($), Outflow ($), Private Reserve actual ($)
  - 2-3 retirement accounts con balance
  - 1-2 non-retirement accounts con balance
  - 1 trust con Zillow value
  - 1 liability con balance + interest rate
- Cálculos automáticos (exact rules from PRD):
  - Excess = Inflow - Outflow
  - Private Reserve Target = 6 × Outflow (skip insurance deductibles for V1)
  - Retirement Total per spouse = sum(retirement accounts of that spouse)
  - Non-Retirement Total = sum(non-retirement) — DOES NOT include trust
  - Grand Total Net Worth = Retirement + Non-Retirement + Trust
  - Liabilities Total = separate display, NOT subtracted from net worth
- Generate SACS PDF (UNO solo, no TCC):
  - Header con client name + date
  - Inflow → Outflow → Private Reserve (boxes + arrows, no perfect circles)
  - Numbers en sus posiciones correctas

## ❌ WON'T BUILD (mencionar en Loom honestamente)
- Client management UI (add/edit/delete)
- TCC chart (más complejo, variable bubble layout)
- Canva export
- Authentication
- Dropbox auto-save / report history
- Database con migraciones (uso dict en memoria o SQLite mínimo)
- Visual polish del PDF (legible y correcto es suficiente)

## 🔍 GAPS noticed in PRD (mencionar en Loom)
1. "Data Point List" document referenced (timestamp 29:14) pero no shared
2. TCC has variable bubbles (1-6 per spouse) — needs dynamic layout strategy
3. Private Reserve formula assumes insurance deductibles are summed — clarify