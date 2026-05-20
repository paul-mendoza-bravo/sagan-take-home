# Sagan Take-Home — AW Client Report Portal (Demo)

A minimal working demo of the financial reporting portal described in the PRD: structured form input → automated calculations → SACS + TCC PDF report (2 pages, one click).

Built under a 2-hour cap. See [SCOPE.md](SCOPE.md) for the explicit scope decisions, what was deliberately left out, and gaps noticed in the PRD.

## Stack

- **FastAPI** + Jinja2 templates (single HTML form)
- **Playwright** (Chromium headless) for HTML → PDF rendering
- **No database** — one client hardcoded in `main.py` for the demo
- Pure Python, no JS framework

## Running locally

```powershell
pip install -r requirements.txt
playwright install chromium
python main.py
```

Then open <http://127.0.0.1:8000>.

> **Note on Windows:** the entry point is `python main.py`, not `uvicorn main:app`. We need to set `WindowsProactorEventLoopPolicy` before uvicorn creates its loop so Playwright can launch its subprocess. Running via `uvicorn` directly (without --reload) also works because the policy is set at the top of `main.py` before the loop starts.

## What's built (V1)

- Form with all balance inputs: Inflow, Outflow, Private Reserve, 2 retirement accounts (with owner per spouse), 1 non-retirement, 1 trust, 1 liability with rate
- Automated calculations per PRD §2b (exact rules from Rebecca, 24:28 / 26:15):
  - Excess = Inflow − Outflow
  - Private Reserve Target = 6 × Outflow
  - Retirement Total **per spouse**
  - Non-Retirement Total — **excludes trust**
  - Grand Total Net Worth = Retirement + Non-Retirement + **Trust**
  - Liabilities Total — separate display, **NOT subtracted from net worth**
- **Two-page PDF** generated in one click:
  - **Page 1 — SACS** (Simple Automated Cash Flow): Inflow / Outflow / Excess / Private Reserve current vs target
  - **Page 2 — TCC** (Total Client Chart): Retirement per spouse, Trust, Non-Retirement, Grand Total, Liabilities (separate)

## What's NOT built (deliberately, per 2h cap)

See [SCOPE.md](SCOPE.md) for the full list. The main omissions:

- Client management UI (add/edit/delete) — 1 client hardcoded
- TCC bubble chart with **variable bubble count** per client (1–6 per spouse, Rebecca 22:00). Current TCC uses styled rounded sections + account pills with the correct data, structure, and grouping. Full dynamic-positioned bubble layout is V1.1.
- Canva export, Dropbox auto-save, authentication, report history
- Database / persistence

## Gaps noticed in the PRD (flagged honestly)

1. The "Data Point List" document (29:14) is referenced as the source-of-truth field map but was not shared. Built from the transcript + PDF descriptions instead.
2. TCC bubble count is variable (1–6 per spouse) — needs a real dynamic layout strategy beyond simple grid.
3. Private Reserve Target formula is "6 × monthly expenses + insurance deductibles" — insurance deductibles weren't modeled in V1 (skipped per scope).

## Files

- `main.py` — FastAPI app, form handler, calculations, inline PDF HTML template, Playwright render
- `templates/form.html` — the input form
- `requirements.txt` — pinned deps
- `SCOPE.md` — explicit pre-build scope decisions
