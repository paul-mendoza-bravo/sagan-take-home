import asyncio
import os
import sys
from datetime import date
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Sagan SACS Demo")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

CLIENT = {
    "name": "John & Jane Sample",
    "spouse_1": "John",
    "spouse_2": "Jane",
}


def fmt(n: float) -> str:
    return f"${n:,.2f}"


@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "client": CLIENT},
    )


@app.post("/generate")
async def generate(
    inflow: float = Form(...),
    outflow: float = Form(...),
    private_reserve: float = Form(...),
    roth_ira_owner: str = Form(...),
    roth_ira_balance: float = Form(...),
    k401_owner: str = Form(...),
    k401_balance: float = Form(...),
    brokerage_balance: float = Form(...),
    trust_zillow_value: float = Form(...),
    mortgage_balance: float = Form(...),
    mortgage_rate: float = Form(...),
):
    excess = inflow - outflow
    private_reserve_target = 6 * outflow

    retirement_accounts = [
        ("Roth IRA", roth_ira_owner, roth_ira_balance),
        ("401K", k401_owner, k401_balance),
    ]
    retirement_by_spouse = {CLIENT["spouse_1"]: 0.0, CLIENT["spouse_2"]: 0.0}
    for _, owner, bal in retirement_accounts:
        retirement_by_spouse[owner] += bal
    retirement_total = sum(retirement_by_spouse.values())

    def _spouse_rows(spouse: str) -> str:
        items = [(n, b) for n, o, b in retirement_accounts if o == spouse]
        if not items:
            return '<div class="row pill"><span class="label" style="color:#999">(no accounts)</span><span></span></div>'
        return "".join(
            f'<div class="row pill"><span class="label">{n}</span><span class="value">{fmt(b)}</span></div>'
            for n, b in items
        )

    s1_rows = _spouse_rows(CLIENT["spouse_1"])
    s2_rows = _spouse_rows(CLIENT["spouse_2"])

    non_retirement_total = brokerage_balance
    grand_total_net_worth = retirement_total + non_retirement_total + trust_zillow_value
    liabilities_total = mortgage_balance

    today = date.today().isoformat()

    html = f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  @page {{ size: Letter; margin: 0.6in; }}
  body {{ font-family: system-ui, sans-serif; color: #222; }}
  h1 {{ margin: 0 0 0.2rem 0; }}
  h2 {{ margin: 1.2rem 0 0.4rem 0; font-size: 1.1rem; border-bottom: 1px solid #999; padding-bottom: 2px; }}
  h3 {{ margin: 0 0 0.4rem 0; font-size: 0.95rem; border-bottom: 1px solid #ccc; padding-bottom: 2px; }}
  .meta {{ color: #666; margin-bottom: 1rem; }}
  .box {{ border: 1px solid #444; padding: 0.6rem 0.8rem; margin: 0.4rem 0; }}
  .row {{ display: flex; justify-content: space-between; padding: 2px 0; }}
  .label {{ color: #444; }}
  .value {{ font-variant-numeric: tabular-nums; }}
  .excess {{ background: #ffe; border: 2px solid #444; font-weight: 600; }}
  .grand {{ font-weight: 700; border-top: 2px solid #444; margin-top: 0.4rem; padding-top: 0.4rem; }}
  .subtotal {{ font-weight: 600; border-top: 1px solid #999; margin-top: 0.3rem; padding-top: 0.3rem; }}
  .note {{ font-style: italic; color: #555; margin-top: 0.4rem; }}
  .page-break {{ page-break-before: always; }}
  .tcc-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-top: 0.5rem; }}
  .tcc-box {{ border: 1.5px solid #444; padding: 0.7rem 0.9rem; border-radius: 14px; }}
  .tcc-box.full {{ grid-column: 1 / -1; }}
  .tcc-box.trust {{ background: #eef3ff; border: 2px solid #2d5a8a; border-radius: 60px; padding: 1rem 1.5rem; text-align: center; }}
  .tcc-box.trust h3 {{ border: none; padding: 0; }}
  .tcc-box.liab {{ border: 2px solid #c43030; background: #fff0f0; border-radius: 14px; }}
  .grand-box {{ margin-top: 0.6rem; border: 2px solid #222; background: #f6f6f6; padding: 0.7rem 0.9rem; border-radius: 12px; }}
  .row.pill {{ border: 1px solid #bbb; border-radius: 999px; padding: 4px 14px; margin: 4px 0; background: #fafafa; }}

  /* SACS visual diagram */
  .sacs-diagram {{ text-align: center; margin: 1.2rem 0 1.5rem; }}
  .sacs-row {{ display: flex; justify-content: center; align-items: center; gap: 1.2rem; }}
  .sacs-circle {{ width: 150px; height: 150px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
  .sacs-circle.inflow {{ background: #2d8a4a; }}
  .sacs-circle.outflow {{ background: #c43030; }}
  .sacs-circle.reserve {{ background: #2d5a8a; margin: 0 auto; }}
  .circle-label {{ font-weight: 700; font-size: 0.85rem; letter-spacing: 1px; }}
  .circle-amount {{ background: white; color: #222; padding: 3px 10px; border-radius: 4px; margin-top: 8px; font-weight: 600; font-size: 0.9rem; }}
  .sacs-arrow {{ font-size: 1.8rem; color: #555; font-weight: 700; }}
  .sacs-arrow-down {{ font-size: 1rem; margin: 0.8rem 0; color: #2d5a8a; font-weight: 600; }}
  .sacs-arrow-down .v {{ font-size: 1.6rem; display: block; line-height: 1; }}
</style></head><body>

<h1>SACS &mdash; Simple Automated Cash Flow</h1>
<div class="meta">Client: {CLIENT['name']} &middot; Date: {today}</div>

<div class="sacs-diagram">
  <div class="sacs-row">
    <div class="sacs-circle inflow">
      <div class="circle-label">INFLOW</div>
      <div class="circle-amount">{fmt(inflow)}</div>
    </div>
    <div class="sacs-arrow">&rarr;</div>
    <div class="sacs-circle outflow">
      <div class="circle-label">OUTFLOW</div>
      <div class="circle-amount">{fmt(outflow)}</div>
    </div>
  </div>
  <div class="sacs-arrow-down">
    <span class="v">&darr;</span>
    Excess: {fmt(excess)}
  </div>
  <div class="sacs-row">
    <div class="sacs-circle reserve">
      <div class="circle-label">PRIVATE<br/>RESERVE</div>
      <div class="circle-amount">{fmt(private_reserve)}</div>
    </div>
  </div>
</div>

<h2>Cash Flow</h2>
<div class="box"><div class="row"><span class="label">Inflow</span><span class="value">{fmt(inflow)}</span></div></div>
<div class="box"><div class="row"><span class="label">Outflow</span><span class="value">{fmt(outflow)}</span></div></div>
<div class="box excess"><div class="row"><span class="label">Excess (Inflow &minus; Outflow)</span><span class="value">{fmt(excess)}</span></div></div>

<h2>Private Reserve</h2>
<div class="box">
  <div class="row"><span class="label">Current balance</span><span class="value">{fmt(private_reserve)}</span></div>
  <div class="row"><span class="label">Target (6 &times; Outflow)</span><span class="value">{fmt(private_reserve_target)}</span></div>
</div>

<div class="page-break"></div>

<h1>TCC &mdash; Total Client Chart</h1>
<div class="meta">Client: {CLIENT['name']} &middot; Date: {today}</div>

<div class="tcc-grid">
  <div class="tcc-box">
    <h3>Retirement &mdash; {CLIENT['spouse_1']}</h3>
    {s1_rows}
    <div class="row subtotal"><span class="label">Subtotal</span><span class="value">{fmt(retirement_by_spouse[CLIENT['spouse_1']])}</span></div>
  </div>
  <div class="tcc-box">
    <h3>Retirement &mdash; {CLIENT['spouse_2']}</h3>
    {s2_rows}
    <div class="row subtotal"><span class="label">Subtotal</span><span class="value">{fmt(retirement_by_spouse[CLIENT['spouse_2']])}</span></div>
  </div>

  <div class="tcc-box trust full">
    <h3>Trust</h3>
    <div class="row"><span class="label">Home (Zillow)</span><span class="value">{fmt(trust_zillow_value)}</span></div>
  </div>

  <div class="tcc-box full">
    <h3>Non-Retirement</h3>
    <div class="row pill"><span class="label">Brokerage</span><span class="value">{fmt(brokerage_balance)}</span></div>
    <div class="row subtotal"><span class="label">Subtotal</span><span class="value">{fmt(non_retirement_total)}</span></div>
  </div>
</div>

<div class="grand-box">
  <div class="row grand" style="border:none; margin:0; padding:0;"><span class="label">Grand Total Net Worth (Retirement + Non-Retirement + Trust)</span><span class="value">{fmt(grand_total_net_worth)}</span></div>
</div>

<h2>Liabilities (separate &mdash; not subtracted)</h2>
<div class="tcc-box liab">
  <div class="row"><span class="label">Mortgage &mdash; balance</span><span class="value">{fmt(mortgage_balance)}</span></div>
  <div class="row"><span class="label">Mortgage &mdash; interest rate</span><span class="value">{mortgage_rate:.2f}%</span></div>
  <div class="row subtotal"><span class="label">Liabilities Total</span><span class="value">{fmt(liabilities_total)}</span></div>
  <div class="note">(NOT subtracted from net worth)</div>
</div>

</body></html>
"""

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        pdf_bytes = await page.pdf(format="Letter", print_background=True)
        await browser.close()
    filename = f"sacs_tcc_{CLIENT['name'].replace(' ', '_').replace('&', 'and')}_{today}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port)
